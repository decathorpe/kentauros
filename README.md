# kentauros

[![Documentation Status](https://readthedocs.org/projects/kentauros/badge/?version=stable)](http://kentauros.readthedocs.io/en/stable/?badge=stable)
[![Documentation Status](https://readthedocs.org/projects/kentauros/badge/?version=latest)](http://kentauros.readthedocs.io/en/latest/?badge=latest)


kentauros is a small, automatable (e.g. systemd timers) build script.

## the following actions are provided:

- `clean`: clean up including sources, exported packages, source packages, etc.)
- `prepare`: get / update / export sources (from git, bzr, url or local file)
- `construct`: assemble source packages from sources (.src.rpm supported)
- `build`: build package locally (mock supported)
- `upload` upload source package to cloud service (copr supported)
- `chain`: sequential execution of all defined package modules

To test out ktr with the provided examples, run in the project base directory
(kentaurosrc in the project directory sets basedir to ./examples automatically):

```sh
./ktr $ACTION --all
```

# working with the code base

To be able to run test scripts and the provided `ktr.py` script, it is necessary
to install some package dependencies, for example on fedora:

- python3-argcomplete
- python3-dateutil
- python3-tinydb
- python3-pylint for generating stats before commits: `./make-stats.sh`
- python3-sphinx for generating and building docs locally: `./make-docs.sh`

Also, since the package examples need certain binaries to work, these packages
might also be necessary:

- bzr, git, wget
- rpm-build, rpmdevtools
- mock
- copr-cli
