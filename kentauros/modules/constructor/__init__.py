from .abstract import Constructor
from .srpm import SrpmConstructor
from ...context import KtrContext
from ...package import KtrPackage


def get_constructor(ctype: str, package: KtrPackage, context: KtrContext) -> Constructor:
    constructor_dict = dict()

    constructor_dict["srpm"] = SrpmConstructor

    return constructor_dict[ctype](package, context)


__all__ = ["get_constructor"]
