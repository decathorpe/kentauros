import configparser as cp
import os


class KtrConfigError(Exception):
    def __init__(self, value: str = ""):
        super().__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class KtrConfig:
    def __init__(self, conf_path: str):
        assert isinstance(conf_path, str)
        self.conf_path = conf_path

        if not os.path.exists(self.conf_path):
            raise FileNotFoundError("The referenced configuration file doesn't exist.")

        if not os.access(self.conf_path, os.R_OK):
            raise IOError("The specified configuration file can't be read.")

        self.conf = cp.ConfigParser(interpolation=None)
        read_path = self.conf.read(self.conf_path)

        if self.conf_path not in read_path:
            raise KtrConfigError("The package configuration file couldn't be parsed successfully.")

    def get(self, section: str, key: str):
        return self.conf.get(section, key)

    def getboolean(self, section: str, key: str):
        return self.conf.getboolean(section, key)
