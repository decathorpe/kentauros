# Known Bugs

## ktr

- missing / malformed configuration values will result in crashes


## builder/mock

- simultaneous mock builds will fail because mock does not support parallel builds


## constructor/srpm

- RPM construction fails when a hyphen is in the version string


## constructor/srpm/rpm_spec

- release string increments _always_, even if base version string is changed

