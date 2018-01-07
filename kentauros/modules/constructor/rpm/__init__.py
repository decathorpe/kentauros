import configparser as cp
import os
import re

from .spec_common import RPMSpecError, format_tag_line
from .spec_preamble_out import get_spec_preamble
from .spec_source_out import get_spec_source
from .spec_version_out import get_spec_version
from ....context import KtrContext
from ....package import KtrPackage
from ....result import KtrResult
from ....shellcmd import ShellCmd


def parse_release(release: str) -> (str, str):
    if "%{dist}" in release:
        parts = release.split("%{dist}")
        part1 = parts[0]
        part2 = "%{dist}" + parts[1]
    else:
        part1 = release
        part2 = ""

    num_string = str()

    for char in part1:
        if char.isnumeric():
            num_string += char
        else:
            break

    abc_string = part1.lstrip("0123456789")

    return num_string, abc_string + part2


class RPMSpec:
    def __init__(self, path: str, package: KtrPackage, context: KtrContext):
        assert isinstance(path, str)
        assert isinstance(package, KtrPackage)
        assert isinstance(context, KtrContext)

        if not os.path.exists(path):
            raise FileNotFoundError()

        self.path = path
        self.package = package
        self.context = context

        try:
            self.stype = self.package.conf.get("modules", "source")
        except cp.NoSectionError:
            self.stype = None
        except cp.NoOptionError:
            self.stype = None
        except KeyError:
            self.stype = None

        with open(path, "r") as file:
            self.contents = file.read()

    def get_lines(self) -> list:
        return self.contents.split("\n")[:-1]

    def get_version(self) -> str:
        for line in self.get_lines():
            assert isinstance(line, str)
            if line[0:8] == "Version:":
                return line.replace("Version:", "").lstrip(" \t").rstrip()

        raise RPMSpecError("No Version tag was found in the file.")

    def get_release(self) -> str:
        for line in self.get_lines():
            assert isinstance(line, str)
            if line[0:8] == "Release:":
                return line.replace("Release:", "").lstrip(" \t").rstrip()

        raise RPMSpecError("No Release tag was found in the file.")

    def set_version(self):
        contents_new = str()

        for line in self.get_lines():
            assert isinstance(line, str)
            if line[0:8] != "Version:":
                contents_new += (line + "\n")
            else:
                contents_new += format_tag_line("Version", self.build_version_string())

        self.contents = contents_new

    def set_source(self):
        contents_new = str()

        for line in self.get_lines():
            assert isinstance(line, str)
            if (line[0:8] != "Source0:") and (line[0:7] != "Source:"):
                contents_new += (line + "\n")
            else:
                if self.stype is not None:
                    contents_new += get_spec_source(self.stype, self.package)

        self.contents = contents_new

    def set_variables(self):
        macro_regex = re.compile("(%global)[ \t]+([a-zA-Z0-9]+)[ \t]+(.+)")

        table = get_spec_preamble(self.stype, self.package, self.context)

        # remove globals that will be set from the spec
        med_contents = str()

        for line in self.get_lines():
            match = macro_regex.match(line)

            if match is None:
                med_contents += (line + "\n")
            else:
                groups = match.groups()
                var = groups[1]

                if var in table.keys():
                    continue
                else:
                    med_contents += (line + "\n")

        # add new globals to the spec
        new_contents = str()

        for var in table.keys():
            new_contents += "%global {} {}\n".format(var, table.get(var))
        new_contents += med_contents

        self.contents = new_contents

    def build_version_string(self) -> str:
        return get_spec_version(self.stype, self.package, self.context)

    def write_to_file(self, path: str):
        assert isinstance(path, str)

        if path == self.path:
            os.remove(path)

        with open(path, "w") as file:
            file.write(self.contents)

    def do_release_reset(self):
        new_rel = str(0) + parse_release(self.get_release())[1]

        contents_new = str()

        for line in self.get_lines():
            if line[0:8] != "Release:":
                assert isinstance(line, str)
                contents_new += (line + "\n")
            else:
                contents_new += format_tag_line("Release", new_rel)

        self.contents = contents_new

    def do_release_bump(self, comment: str = None) -> KtrResult:
        ret = KtrResult(name="RPM .spec Handler")

        if not os.path.exists(self.path):
            raise FileNotFoundError()

        if comment is None:
            comment = "Automatic build by kentauros."

        # construct rpmdev-bumpspec command
        cmd = list()

        # add --verbose or --quiet depending on settings
        if self.context.debug:
            cmd.append("--verbose")

        cmd.append(self.path)
        cmd.append('--comment=' + comment)

        ret.messages.cmd(cmd)

        self.write_to_file(self.path)

        res = ShellCmd("rpmdev-bumpspec").command(*cmd).execute()
        ret.collect(res)

        with open(self.path, "r") as file:
            self.contents = file.read()

        if not res.success:
            ret.messages.log("Release tag in the RPM .spec could not be bumped correctly.")
            return ret.submit(False)

        return ret


__all__ = ["parse_release", "RPMSpec"]
