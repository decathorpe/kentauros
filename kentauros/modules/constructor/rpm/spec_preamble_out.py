from ....context import KtrContext
from ....package import KtrPackage
from ....result import KtrResult


def _spec_preamble_git(package: KtrPackage, context: KtrContext) -> KtrResult:
    assert isinstance(package, KtrPackage)
    assert isinstance(context, KtrContext)

    ret = KtrResult()
    state = context.state.read(package.conf_name)

    commit: str = state["git_last_commit"]
    dt_string: str = state["git_last_date"]
    dt = dt_string.split(" ")

    date = dt[0]
    time = dt[1]

    commit_define = "%global commit " + commit + "\n"
    shortcommit_define = "%global shortcommit %(c=%{commit}; echo ${c:0:7})" + "\n"
    date_define = "%global date " + date + "\n"
    time_define = "%global time " + time + "\n"

    ret.value = commit_define + shortcommit_define + date_define + time_define + "\n"
    return ret.submit(True)


def _spec_preamble_url(package: KtrPackage, context: KtrContext) -> KtrResult:
    assert isinstance(package, KtrPackage)
    assert isinstance(context, KtrContext)

    return KtrResult(True, "")


def _spec_preamble_local(package: KtrPackage, context: KtrContext) -> KtrResult:
    assert isinstance(package, KtrPackage)
    assert isinstance(context, KtrContext)

    return KtrResult(True, "")


def get_spec_preamble(srctype: str, package: KtrPackage, context: KtrContext) -> KtrResult:
    spec_preambles = dict()

    spec_preambles["git"] = _spec_preamble_git
    spec_preambles["local"] = _spec_preamble_local
    spec_preambles["url"] = _spec_preamble_url

    return spec_preambles[srctype](package, context)
