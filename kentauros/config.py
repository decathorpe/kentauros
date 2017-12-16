import configparser as cp
import os

from .context import KtrContext


class KtrConfigError(Exception):
    def __init__(self, value: str = ""):
        super().__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class KtrConfig:
    def __init__(self, context: KtrContext, conf_path: str):
        assert isinstance(context, KtrContext)
        assert isinstance(conf_path, str)

        self.context = context
        self.conf_path = self.conf_path

        if not os.path.exists(self.conf_path):
            raise FileNotFoundError("The referenced configuration file doesn't exist.")

        if not os.access(self.conf_path, os.R_OK):
            raise IOError("The specified configuration file can't be read.")

        self.conf = cp.ConfigParser()
        read_path = self.conf.read(self.conf_path)

        if read_path != self.conf_path:
            raise KtrConfigError("The package configuration file couldn't be parsed successfully.")

    def get(self, section: str, key: str):
        return self.conf.get(section, key)

    def getboolean(self, section: str, key: str):
        return self.conf.getboolean(section, key)
