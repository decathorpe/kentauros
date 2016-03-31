"""
This module contains common code for entry point functions. At this moment, this
only includes the :py:func:`get_action_args` function.
"""


from kentauros.definitions import ActionType

from kentauros.init.cli import CLIArgs
from kentauros.package import Package


def get_action_args(cli_args: CLIArgs,
                    pkgname: str,
                    action_type_enum: ActionType) -> tuple:
    """
    This function returns arguments for an Action() constructor as tuple.
    It only constructs Package() objects as needed.

    Arguments:
        cli_args (CLIArgs): parsed command line arguments
        pkgname (str): name of package the action will be executed for
        action_type_enum (ActionType): specifies the type of Action

    Returns:
        tuple: :py:class:`kentauros.action.Action` Constructor arguments
    """

    assert isinstance(cli_args, CLIArgs)
    assert isinstance(pkgname, str)
    assert isinstance(action_type_enum, ActionType)

    action_args_dict = dict()
    action_args_dict[ActionType.BUILD] = (cli_args.get_force(),)
    action_args_dict[ActionType.CHAIN] = (cli_args.get_force(),)
    action_args_dict[ActionType.CLEAN] = (cli_args.get_force(),)
    action_args_dict[ActionType.CONSTRUCT] = (cli_args.get_force(),)
    action_args_dict[ActionType.EXPORT] = (cli_args.get_force(),)
    action_args_dict[ActionType.GET] = (cli_args.get_force(),)
    action_args_dict[ActionType.REFRESH] = (cli_args.get_force(),)
    action_args_dict[ActionType.STATUS] = (cli_args.get_force(),)
    action_args_dict[ActionType.UPDATE] = (cli_args.get_force(),)
    action_args_dict[ActionType.UPLOAD] = (cli_args.get_force(),)
    action_args_dict[ActionType.VERIFY] = (cli_args.get_force(),)

    if action_type_enum == ActionType.CONFIG:
        action_args_dict[ActionType.CONFIG] = (cli_args.get_force(),
                                               cli_args.get_config_section(),
                                               cli_args.get_config_key(),
                                               cli_args.get_config_value())

    action_args_dict[ActionType.CREATE] = (cli_args.get_force(),)

    if action_type_enum == ActionType.CREATE:
        return (pkgname,) + action_args_dict[ActionType.CREATE]
    else:
        return (Package(pkgname),) + action_args_dict[action_type_enum]

