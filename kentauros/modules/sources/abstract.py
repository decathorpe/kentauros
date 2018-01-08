import abc
import os
import shutil

from kentauros.context import KtrContext
from kentauros.modules.module import KtrModule
from kentauros.package import KtrPackage
from kentauros.result import KtrResult


class Source(KtrModule, metaclass=abc.ABCMeta):
    def __init__(self, package: KtrPackage, context: KtrContext):
        super().__init__(package, context)
        self.updated = False

        self.sdir = os.path.join(self.context.get_datadir(), self.package.conf_name)

        self.dest = None
        self.stype = None

        self.actions["export"] = self.export
        self.actions["get"] = self.get
        self.actions["prepare"] = self.execute
        self.actions["refresh"] = self.refresh
        self.actions["update"] = self.update

    @abc.abstractmethod
    def get_orig(self) -> str:
        pass

    @abc.abstractmethod
    def get_keep(self) -> bool:
        pass

    @abc.abstractmethod
    def export(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def get(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def update(self) -> KtrResult:
        pass

    @abc.abstractmethod
    def status(self) -> KtrResult:
        pass

    def clean(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        if not os.path.exists(self.sdir):
            ret.messages.log("Nothing here to be cleaned.")
            return ret.submit(True)

        # try to be careful with "rm -r"
        try:
            assert os.path.isabs(self.dest)
            assert self.context.get_datadir() in self.dest
        except AssertionError as error:
            ret.messages.log("Source directory looked suspicious, not recursively deleting. Error:")
            ret.messages.log(str(error))
            return ret.submit(False)

        # remove source destination first

        # get source files from state
        status = self.context.state.read(self.package.conf_name)

        try:
            source_files = status["source_files"]
        except KeyError:
            source_files = []

        # if destination is a file (tarball):
        if os.path.isfile(self.dest):
            os.remove(self.dest)
            file = os.path.basename(self.dest)
            ret.messages.log("Removed file: '{}'".format(file))

            if file in source_files:
                source_files.remove(file)

        # if destination is a directory (VCS repo):
        elif os.path.isdir(self.dest):
            shutil.rmtree(self.dest)
            ret.messages.log("Removed directory: '{}'".format(os.path.basename(self.dest)))

        # check all other files:
        for file in source_files:
            path = os.path.join(self.sdir, file)

            if os.path.exists(path):
                os.remove(path)
                ret.messages.log("Removed file: '{}'".format(file))
                source_files.remove(file)

        ret.state["source_files"] = source_files

        # if source directory is empty now (no patches, additional files, etc. left):
        # remove whole directory
        if not os.listdir(self.sdir):
            os.rmdir(self.sdir)
            ret.messages.log("Removed sources directory.")

        return ret.submit(True)

    def formatver(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        version_format = self.package.conf.get("source", "version")

        ret.value = version_format
        ret.state["version_format"] = version_format
        return ret.submit(True)

    def execute(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        force = self.context.get_force()
        old_status = self.status()

        res = self.get()
        ret.collect(res)

        if res.success:
            new_status = self.status()

            if new_status == old_status:
                ret.messages.log(
                    "The downloaded Source is not newer than the last known source state.")
                return ret.submit(False)
            else:
                self.updated = True
                res = self.export()
                ret.collect(res)
                return res.submit(res.success)

        res = self.update()
        ret.collect(res)

        if res.success:
            new_status = self.status()

            if new_status == old_status:
                ret.messages.log(
                    "The \"updated\" Source is not newer than the last known source state.")
                return ret.submit(False)
            else:
                self.updated = True
                res = self.export()
                ret.collect(res)
                return ret.submit(res.success)

        if force:
            ret.messages.log("Force-Exporting the Sources despite no source changes.")
            res = self.export()
            ret.collect(res)
            return ret.submit(res.success)

        ret.messages.log("The Source did not change.")
        return ret.submit(False)

    def refresh(self) -> KtrResult:
        ret = KtrResult(name=self.name())

        res = self.clean()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Source cleanup not successful. Not getting sources again.")
            return ret.submit(False)

        res = self.get()
        ret.collect(res)

        if not res.success:
            ret.messages.log("Source getting not successful.")
            return ret.submit(False)

        # everything successful:
        return ret.submit(True)
