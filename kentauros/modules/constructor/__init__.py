"""
This subpackage contains the abstract :py:class:`Constructor` base class and
:py:class:`DummyConstructor` and :py:class:`SrpmConstructor` subclass definitions. They contain
methods for building sources into buildable packages. Additionally, this file contains a dictionary
which maps :py:class:`kentauros.definitions.ConstructorType` enums to their respective class
constructors.
"""


from kentauros.definitions import ConstructorType

from kentauros.modules.constructor.abstract import Constructor
from kentauros.modules.constructor.srpm import SrpmConstructor


def get_constructor(ctype: ConstructorType, package) -> Constructor:
    """
    This function constructs a `Constructor` from a `ConstructorType` enum member and a package.
    """

    constructor_dict = dict()

    constructor_dict[ConstructorType.SRPM] = SrpmConstructor

    return constructor_dict[ctype](package)
