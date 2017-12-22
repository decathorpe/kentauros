import configparser as cp
import os
import shutil

from .result import KtrResult


class KtrValidator:
    def __init__(self, config: cp.ConfigParser, section: str, keys: list = None,
                 binaries: list = None, files: list = None):

        assert isinstance(config, cp.ConfigParser)
        assert isinstance(section, str)

        if keys is None:
            keys = []

        assert isinstance(keys, list)
        for key in keys:
            assert isinstance(key, str)

        if binaries is None:
            binaries = []

        assert isinstance(binaries, list)
        for binary in binaries:
            assert isinstance(binary, str)

        if files is None:
            files = []

        assert isinstance(files, list)
        for file in files:
            assert isinstance(file, str)

        self.config = config
        self.section = section
        self.keys = keys
        self.binaries = binaries
        self.files = files

    def validate(self) -> KtrResult:
        ret = KtrResult()
        success = True

        # check for expected sections and keys in the config file
        if self.section not in self.config:
            template = "The section '{}' doesn't exist in the package configuration."
            ret.messages.err(template.format(self.section))
            success = False
        else:
            for key in self.keys:
                if key not in self.config[self.section]:
                    template = "The section '{}' of the package configuration doesn't set '{}'."
                    ret.messages.err(template.format(self.section, key))
                    success = False

        # check for the presence of expected binaries
        for binary in self.binaries:
            if shutil.which(binary) is None:
                template = "The required binary '{}' has not been found in $PATH."
                ret.messages.err(template.format(binary))
                success = False

        # check for the presence of expected files
        for file in self.files:
            if not os.path.exists(file):
                template = "The required file '{}' has not been found."
                ret.messages.err(template.format(file))
                success = False

        return ret.submit(success)
