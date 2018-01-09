from collections import OrderedDict

from kentauros.package import KtrPackage


def _spec_preamble_git(package: KtrPackage) -> OrderedDict:
    assert isinstance(package, KtrPackage)

    state = package.context.state.read(package.conf_name)

    commit: str = state["git_last_commit"]
    dt_string: str = state["git_last_date"]
    dt = dt_string.split(" ")

    date = dt[0]
    time = dt[1]

    preamble = OrderedDict()
    preamble["commit"] = commit
    preamble["shortcommit"] = "%(c=%{commit}; echo ${c:0:7})"
    preamble["date"] = date
    preamble["time"] = time

    return preamble


def _spec_preamble_url(package: KtrPackage) -> OrderedDict:
    assert isinstance(package, KtrPackage)

    preamble = OrderedDict()
    return preamble


def _spec_preamble_local(package: KtrPackage) -> OrderedDict:
    assert isinstance(package, KtrPackage)
    preamble = OrderedDict()
    return preamble


def get_spec_preamble(srctype: str, package: KtrPackage) -> OrderedDict:
    spec_preambles = dict()

    spec_preambles["git"] = _spec_preamble_git
    spec_preambles["local"] = _spec_preamble_local
    spec_preambles["url"] = _spec_preamble_url

    return spec_preambles[srctype](package)
