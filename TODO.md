# TODO items for kentauros

## ktr

- add assertions for type checks (if debug: assert isinstance)


## actions:

- status: implementation missing
- upload: missing error handling
- verify: implementation missing
- remove unnecessary action classes


## conntest:

- rework submodule
- close socket after use
- try connecting at least 3 times within 10 seconds or something


## construct+build:

- srpm: move .spec.old back into place if builds fail


## construct:

- rework relreset / force code so it actually works as intended


## definitions:

- rework submodule


## init:

- rework subpackage
- cli: add --message argument for supplying changelog messages


## instance:

- rework submodule
- remove old log,err,dbg,log_command functions


## package:

- rework submodule
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

- rework subpackage
- copr: missing error handling
