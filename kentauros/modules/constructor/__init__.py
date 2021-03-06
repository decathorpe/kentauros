from kentauros.context import KtrContext
from kentauros.package import KtrPackage
from .abstract import Constructor
from .srpm import SrpmConstructor


def get_constructor(ctype: str, package: KtrPackage, context: KtrContext) -> Constructor:
    constructor_dict = dict()

    constructor_dict["srpm"] = SrpmConstructor

    return constructor_dict[ctype](package, context)


__all__ = ["get_constructor"]
