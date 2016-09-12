# TODO items for kentauros

## ktr

- add assertions for type checks (if debug: assert isinstance)


## actions:

- status: implementation missing
- upload: missing error handling
- verify: implementation missing
- remove unnecessary action classes


## construct+build:

- srpm: move .spec.old back into place if builds fail


## construct:

- rework relreset / force code so it actually works as intended


## init:

- rework subpackage
- cli: add --message argument for supplying changelog messages


## instance:

- remove old log,err,dbg,log_command functions


## package:

- at initialisation, replace hyphens in source/version with tilde
- allow variables in package configuration file: `$(VERSION)`, `$(NAME)`


## pkgformat:

- rework subpackage
- finish RPM spec handling rewrite


## source:

- bzr: lightweight checkouts are not supported yet


## state:

- rework subpackage


## upload:

- copr: missing error handling
