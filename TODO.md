# TODO items for kentauros


These TODO items complement those found within the code itself.


## ktr

- add exports directory to initialisation (for built binary packages)
- add assertions for type checks (if debug: assert isinstance)


## actions:

- status: implementation missing
- upload: missing error handling
- verify: implementation missing


## builder:

- mock: export successfully built RPM packages to basedir/exports


## conntest:

- close socket after use
- try connecting at least 3 times within 10 seconds or something


## construct+build:

- srpm: move .spec.old back into place if builds fail


## init:

- cli: add --message argument for supplying changelog messages


## package:

- at initialisation, replace hyphens in source/version with tilde
- allow variables in package configuration file: `$(VERSION)`, `$(NAME)`


## source:

- bzr: lightweight checkouts are not supported yet

