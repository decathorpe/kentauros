from .abstract import Exporter
from .createrepo import CreateRepoExporter
from ...context import KtrContext
from ...package import KtrPackage


def get_exporter(ctype: str, package: KtrPackage, context: KtrContext) -> Exporter:
    exporter_dict = dict()

    exporter_dict["createrepo"] = CreateRepoExporter

    return exporter_dict[ctype](package, context)


__all__ = ["get_exporter"]
