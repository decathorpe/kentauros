# kentauros

[![Documentation Status](https://readthedocs.org/projects/kentauros/badge/?version=stable)](http://kentauros.readthedocs.io/en/stable/?badge=stable)
[![Documentation Status](https://readthedocs.org/projects/kentauros/badge/?version=latest)](http://kentauros.readthedocs.io/en/latest/?badge=latest)


kentauros is a small, automatable (e.g. systemd timers) build script.

## the following actions are supported at the moment:

- clean up files: `clean` action
- prepare sources (git, bzr, url, local)
- construct source packages from sources (.src.rpm supported): construct` action
- build locally (mock supported): `build` action
- upload source packages to cloud build services (copr supported): `upload` action
- execute all defined package modules sequentially: `chain` action

To test out ktr with the provided examples, run in the project base directory (kentaurosrc in
project directory sets basedir to ./examples automatically):

```sh
./ktr $ACTION --all
```

# working with the code base

To be able to run test scripts and the provided `ktr.py` script, it is necessary to install some
packages:

- python3-argcomplete
- python3-dateutil
- python3-pylint for generating and updating stats before commits
- python3-sphinx for generating and building docs locally
- python3-tinydb

Also, since the package examples need certain binaries to work, these packages might also be
necessary:

- bzr, git, wget
- rpm-build, rpmdevtools
- mock
- copr-cli
