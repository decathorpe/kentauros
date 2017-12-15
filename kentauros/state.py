import os

from tinydb import TinyDB, Query


def _dict_is_subset(sup: dict, sub: dict) -> bool:
    if sup == dict():
        return False

    for key in sub.keys():
        # if the key is not yet present: update
        if key not in sup.keys():
            return False

        # if the values for the same key are different: update
        if sub[key] != sup[key]:
            return False

    # if all keys and values for existing keys are identical: don't update
    return True


class KtrState:
    def __init__(self, path: str):
        assert isinstance(path, str)
        assert os.path.exists(path)
        assert os.access(path, os.R_OK)

        self.path = path

    def read(self, conf_name: str) -> dict:
        assert isinstance(conf_name, str)

        with TinyDB(self.path, indent=4, sort_keys=True) as db:
            package = Query()
            results = db.search(package.name == conf_name)

        if len(results) == 0:
            return dict()
        else:
            return results[0]

    def write(self, conf_name: str, entries: dict):
        assert isinstance(conf_name, str)
        assert isinstance(entries, dict)

        if entries == dict():
            return

        old_state = self.read(conf_name)
        if _dict_is_subset(old_state, entries):
            return

        with TinyDB(self.path, indent=4, sort_keys=True) as db:
            package = Query()

            if old_state == dict():
                entries["name"] = conf_name
                db.insert(entries)
            else:
                db.update(entries, package.name == conf_name)

    def remove(self, conf_name):
        assert isinstance(conf_name, str)

        with TinyDB(self.path, indent=4, sort_keys=True) as db:
            package = Query()
            db.remove(package.name == conf_name)
