from kentauros.config import KtrTestConfig
from kentauros.context import KtrTestContext
from kentauros.package import KtrTestPackage

TEST_PACKAGE_GIT_SOURCE = KtrTestPackage(
    "testpackage",
    KtrTestContext(state={
        "testpackage": {
            "name": "testpackage",
            "version": "1.0",
            "git_last_commit": "5b88c95c45e91781aed441c446210c6979350c3f",
            "git_last_date": "20160820 083657",
            "git_ref": "master",
            "srpm_last_version": "1.0",
            "srpm_last_release": "1%{?dist}",
            "source_files": ["testpackage-1.0~20160820.083657.git5b88c95.tar.gz"]}}),
    KtrTestConfig({
        "package": {
            "name": "testpackage",
            "version": "1.0",
            "release": "pre",
            "modules": "source,constructor"},
        "modules": {"source": "git",
                    "constructor": "srpm"},
        "git": {"keep": "True",
                "keep_repo": "True",
                "orig": "https://github.com/decathorpe/testpackage",
                "ref": "master",
                "shallow": "False"},
        "srpm": {}}))

TEST_PACKAGE_URL_SOURCE = KtrTestPackage(
    "testpackage",
    KtrTestContext(state={
        "testpackage": {
            "name": "testpackage",
            "version": "1.0",
            "url_last_version": "1.0",
            "srpm_last_version": "1.0",
            "srpm_last_release": "1%{?dist}",
            "source_files": ["testpackage-1.0.tar.gz"]}}),
    KtrTestConfig({
        "package": {
            "name": "testpackage",
            "version": "1.0",
            "release": "stable",
            "modules": "source,constructor"},
        "modules": {"source": "url",
                    "constructor": "srpm"},
        "url": {"keep": "True",
                "orig": "https://decathorpe.com/testpackage/1.0/testpackage-1.0.tar.gz"},
        "srpm": {}}))

TEST_PACKAGE_LOCAL_SOURCE = KtrTestPackage(
    "testpackage",
    KtrTestContext(state={
        "testpackage": {
            "name": "testpackage",
            "version": "1.0",
            "srpm_last_version": "1.0",
            "srpm_last_release": "1%{?dist}",
            "source_files": ["testpackage-1.0.tar.gz"]}}),
    KtrTestConfig({
        "package": {
            "name": "testpackage",
            "version": "1.0",
            "release": "stable",
            "modules": "source,constructor"},
        "modules": {"source": "local",
                    "constructor": "srpm"},
        "local": {"keep": "True",
                  "orig": "/usr/local/src/testpackage/1.0/testpackage-1.0.tar.gz"},
        "srpm": {}}))
