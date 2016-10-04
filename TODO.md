# TODO items for kentauros

## actions:

- import: implementation missing
- status: implementation missing
- upload: missing error handling
- remove unnecessary action classes


## construct+build:

- srpm: move .spec.old back into place if builds fail


## construct:

- srpm: test if relreset / force code actually works as intended now
- srpm: return statistics about build as status
- srpm: implement meta-method that calls all methods in correct order


## import:

- get package status from all modules


## package:

- allow variables in package configuration file: `$(VERSION)`, `$(NAME)`


## pkgformat/rpm:

- error handling of `rpmdev-bumpspec` subprocess
- write URL of Source to Spec at `Source0` line if the source is a `UrlSource`


## source:

- bzr: lightweight checkouts are not supported yet
- url: support curl and check at runtime which downloader can be used


## upload:

- copr: missing error handling
