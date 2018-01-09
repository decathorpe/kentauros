import configparser as cp

from .meta_config import KtrConfig


class KtrTestConfig(KtrConfig):
    def __init__(self, values: dict):
        super().__init__()

        self.values = values

        self.conf = cp.ConfigParser()
        self.conf.read_dict(values)

    def get(self, section: str, key: str):
        return self.values[section][key]

    def getboolean(self, section: str, key: str):
        return bool(self.values[section][key])
