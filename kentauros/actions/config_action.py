"""
This submodule contains the actions used by a invocation of the `ktr-config`
script.
"""


from kentauros.definitions import ActionType
from kentauros.instance import log

from kentauros.package import Package
from kentauros.actions.common import Action, LOGPREFIX1


class ConfigAction(Action):
    """
    This `Action` subclass contains information for changing package
    configuration values stored in the package's \\*.conf file.

    Arguments:
        Package kpkg:       Package instance configuration will be changed for
        bool force:         currently without effect
        str section:        section of conf file that `key` is in
        str key:            key that `value` will be written to
        str value:          value that will be set in configuration

    Attributes:
        ActionType atype:   here: stores `ActionType.CONFIG`
        str section:        stores `section` given at initialisation
        str key:            stores `key` given at initialisation
        str value:          stores `value` given at initialisation
    """

    def __init__(self, kpkg: Package, force: bool,
                 section: str, key: str, value: str):
        super().__init__(kpkg, force)
        self.atype = ActionType.CONFIG

        self.section = section
        self.key = key
        self.value = value

    def execute(self) -> bool:
        """
        This method checks if the specified section already exists in the
        configuration file - and creates it, if it doesn't. Following this
        check, it will change or add `section`/`key` to `value` in the
        :py:class:`configparser.ConfigParser` object and then writes the changed
        configuration back to the package's \\*.conf file.

        Returns:
            bool:           always *True* at the moment
        """

        if self.section not in self.kpkg.conf.sections():
            self.kpkg.conf.add_section(self.section)

        self.kpkg.conf.set(self.section, self.key, self.value)
        self.kpkg.update_config()

        log(LOGPREFIX1 + "Configuration value changed: ", 2)
        log(LOGPREFIX1 + self.kpkg.name + ".conf: " +
            self.section + "/" + self.key + ": " + self.value, 2)

        return True

