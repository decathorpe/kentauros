import os

from kentauros.package import KtrPackage
from .spec_common import format_tag_line


def _spec_source_git(package: KtrPackage) -> str:
    assert isinstance(package, KtrPackage)

    src_str = format_tag_line("Source0", "%{name}-%{version}.tar.gz")

    return src_str


def _spec_source_local(package: KtrPackage) -> str:
    assert isinstance(package, KtrPackage)

    src_str = format_tag_line("Source0", os.path.basename(package.conf.get("local", "orig")))
    return src_str


def _spec_source_url(package: KtrPackage) -> str:
    assert isinstance(package, KtrPackage)

    src_str = format_tag_line("Source0", package.conf.get("url", "orig"))
    return src_str


def get_spec_source(srctype: str, package: KtrPackage) -> str:
    spec_sources = dict()

    spec_sources["git"] = _spec_source_git
    spec_sources["local"] = _spec_source_local
    spec_sources["url"] = _spec_source_url

    return spec_sources[srctype](package)
