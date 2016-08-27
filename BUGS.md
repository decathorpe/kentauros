# Known Bugs

## ktr

- missing / malformed configuration values will result in crashes
- package that has no source download / update will result in exit(1)
- no information (besides last build version and last build release) is stored
  between builds -> implement small database for state storage (basedir/state.db)


## ktr/actions

- clean action removes patches in the package source directory, too -> only remove
  the entire sources/name directory if it's empty after removing `source.dest`


## build/mock

- empty dist string in configuration crashes kentauros


## constructor/srpm

- RPM construction fails when a hyphen is in the version string
- force-constructing SRPM from URL sources results in "new snapshot" changelog msg

