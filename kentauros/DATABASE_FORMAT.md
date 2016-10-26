# kentauros state database format

# This is bound to change in the future

The column names are derived from the relevant section and key names in the
package configuration file, with sections and keys separated by an underscore.

The following columns are expected to be there, regardless of package-specific
settings, because they identify the package:

- `id`: automatically added by tinydb
- `name`: name of the configuration file without suffix
- `package_name`: name of the actual package
- `source_type`: type of upstream source
- `source_version`: upstream source version

These are only expected if their corresponding source type has been set:

- `git_branch`: branch set in package configuration
- `git_commit`: git commit hash set in package configuration
- `git_last_commit`: commit hash after the latest source change
- `git_last_date`: date and time of latest commit
- `bzr_branch`: branch set in package configuration
- `bzr_rev`: revision number set in package configuration
- `bzr_last_rev`: revision number after the latest source change

For RPM packages, the following columns are also expected:

- `rpm_last_release`: release string of the latest built package
