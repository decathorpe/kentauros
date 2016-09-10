# Known Bugs

## ktr

- missing / malformed configuration values will result in crashes
- package that has no source download / update will result in exit(1)


## constructor/srpm

- RPM construction fails when a hyphen is in the version string
- force-constructing SRPM from URL sources results in "new snapshot" changelog msg
