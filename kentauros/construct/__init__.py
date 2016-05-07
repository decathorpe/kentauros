"""
This subpackage contains the abstract :py:class:`Constructor` base class and
:py:class:`DummyConstructor` and :py:class:`SrpmConstructor` subclass
definitions. They contain methods for building sources into buildable packages.
Additionally, this file contains a dictioary which maps
:py:class:`kentauros.definitions.ConstructorType` enums to their respective
class constructors.
"""


from kentauros.definitions import ConstructorType

from kentauros.construct.con_dummy import DummyConstructor
from kentauros.construct.con_srpm import SrpmConstructor


CONSTRUCTOR_TYPE_DICT = dict()
""" This dictionary maps `ConstructorType` enum members to their respective
`Constructor` subclass constructors.
"""

CONSTRUCTOR_TYPE_DICT[ConstructorType.NONE] = DummyConstructor
CONSTRUCTOR_TYPE_DICT[ConstructorType.SRPM] = SrpmConstructor

