"""
This subpackage contains the :py:class:`Constructor` base class and
:py:class:`SrpmConstructor` subclass definitions. They contain methods for
building sources into buildable packages. Additionally, this file contains a
dictioary which maps :py:class:`kentauros.definitions.ConstructorType`
enums to their respective class constructors.
"""


from kentauros.definitions import ConstructorType

from kentauros.construct.constructor import Constructor
from kentauros.construct.srpm import SrpmConstructor


__all__ = ["rpm_spec", "constructor", "srpm"]


CONSTRUCTOR_TYPE_DICT = dict()
""" This dictionary maps `ConstructorType` enum members to their respective
`Constructor` subclass constructors.
"""

CONSTRUCTOR_TYPE_DICT[ConstructorType.NONE] = Constructor
CONSTRUCTOR_TYPE_DICT[ConstructorType.SRPM] = SrpmConstructor

