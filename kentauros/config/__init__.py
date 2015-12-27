"""
kentauros.config module
explicitly determines order in which configurations are read.
later items in the list can override already determined configuration,
or act as fallback if none has been found so far.
"""


from kentauros.config import cli, default, envvar, project, system, user

KTR_CONF_LIST = [default.CONF,
                 system.CONF,
                 user.CONF,
                 project.CONF,
                 env.CONF,
                 cli.CONF]

