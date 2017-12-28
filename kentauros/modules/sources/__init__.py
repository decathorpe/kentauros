from ...context import KtrContext
from ...package import KtrPackage

from .abstract import Source
from .git import GitSource
from .url import UrlSource
from .local import LocalSource


def get_source(stype: str, package: KtrPackage, context: KtrContext) -> Source:
    source_dict = dict()

    source_dict["git"] = GitSource
    source_dict["local"] = LocalSource
    source_dict["url"] = UrlSource

    return source_dict[stype](package, context)


__all__ = ["get_source"]
