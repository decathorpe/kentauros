from kentauros.package import KtrPackage


def _spec_version_git(package: KtrPackage) -> str:
    assert isinstance(package, KtrPackage)

    template: str = package.context.conf.get("main", "version_template_git")

    if "%{version}" in template:
        template = template.replace("%{version}", package.get_version())
    if "%{version_sep}" in template:
        template = template.replace("%{version_sep}", package.get_version_separator())

    return template


def _spec_version_local(package: KtrPackage) -> str:
    assert isinstance(package, KtrPackage)

    ver_str = package.get_version()
    return ver_str


def _spec_version_url(package: KtrPackage) -> str:
    assert isinstance(package, KtrPackage)

    ver_str = package.get_version()
    return ver_str


def get_spec_version(srctype: str, package: KtrPackage) -> str:
    spec_versions = dict()

    spec_versions["git"] = _spec_version_git
    spec_versions["local"] = _spec_version_local
    spec_versions["url"] = _spec_version_url

    return spec_versions[srctype](package)
