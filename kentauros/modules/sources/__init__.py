from kentauros.context import KtrContext
from kentauros.package import KtrPackage
from .abstract import Source
from .git import GitSource
from .local import LocalSource
from .url import UrlSource


def get_source(stype: str, package: KtrPackage, context: KtrContext) -> Source:
    source_dict = dict()

    source_dict["git"] = GitSource
    source_dict["local"] = LocalSource
    source_dict["url"] = UrlSource

    return source_dict[stype](package, context)


__all__ = ["get_source"]
