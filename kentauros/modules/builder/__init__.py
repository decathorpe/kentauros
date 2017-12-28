from .abstract import Builder
from .mock import MockBuilder
from ...context import KtrContext
from ...package import KtrPackage


def get_builder(btype: str, package: KtrPackage, context: KtrContext) -> Builder:
    builder_dict = dict()

    builder_dict["mock"] = MockBuilder

    return builder_dict[btype](package, context)


__all__ = ["get_builder"]
