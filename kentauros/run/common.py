"""
common code for run() entry points
"""

from kentauros.definitions import ActionType
from kentauros.package import Package


def get_action_args(cli_args, pkgname, action_type_enum):
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

    assert isinstance(action_type_enum, ActionType)

    action_args_dict = dict()
    action_args_dict[ActionType.BUILD] = (cli_args.force,)
    action_args_dict[ActionType.CHAIN] = (cli_args.force,)
    action_args_dict[ActionType.CLEAN] = (cli_args.force,)
    action_args_dict[ActionType.CONSTRUCT] = (cli_args.force,)
    action_args_dict[ActionType.EXPORT] = (cli_args.force,)
    action_args_dict[ActionType.GET] = (cli_args.force,)
    action_args_dict[ActionType.REFRESH] = (cli_args.force,)
    action_args_dict[ActionType.STATUS] = (cli_args.force,)
    action_args_dict[ActionType.UPDATE] = (cli_args.force,)
    action_args_dict[ActionType.UPLOAD] = (cli_args.force,)
    action_args_dict[ActionType.VERIFY] = (cli_args.force,)

    if action_type_enum == ActionType.CONFIG:
        action_args_dict[ActionType.CONFIG] = (cli_args.force,
                                               cli_args.config_section,
                                               cli_args.config_key,
                                               cli_args.config_value)

    action_args_dict[ActionType.CREATE] = (cli_args.force,)

    if action_type_enum == ActionType.CREATE:
        return (pkgname,) + action_args_dict[ActionType.CREATE]
    else:
        return (Package(pkgname),) + action_args_dict[action_type_enum]

