from .abstract import Uploader
from .copr import CoprUploader
from ...context import KtrContext
from ...package import KtrPackage


def get_uploader(utype: str, package: KtrPackage, context: KtrContext) -> Uploader:
    uploader_dict = dict()

    uploader_dict["copr"] = CoprUploader

    return uploader_dict[utype](package, context)


__all__ = ["get_uploader"]
