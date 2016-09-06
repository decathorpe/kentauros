# kentauros

[![Documentation Status](https://readthedocs.org/projects/kentauros/badge/?version=stable)](http://kentauros.readthedocs.io/en/stable/?badge=stable)
[![Documentation Status](https://readthedocs.org/projects/kentauros/badge/?version=latest)](http://kentauros.readthedocs.io/en/latest/?badge=latest)


kentauros is a small, automatable (e.g. systemd timers) build script.

## the following actions are supported at the moment:

- get sources from specified location (git, bzr, url supported): ```get``` action
- update sources (git, bzr supported): ```update``` action
- clean sources (git, bzr, url supported): ```clean``` action
- clean and re-get sources (git, bzr, url supported): ```refresh``` action
- export sources to tarball (git, bzr supported): ```export``` action
- construct source packages from sources (.src.rpm supported): ```construct``` action
- build locally (mock supported): ```build``` action
- upload source packages to cloud build services (copr supported): ```upload``` action
- execute them consecutively, depending on present updates: ```chain``` action
- create package configuration files from template: ```ktr-create``` script

To test out ktr with the provided examples, run in the project base directory
(kentaurosrc in project directory sets basedir to ./examples automatically):

```sh
./ktr $ACTION --all
./ktr-create test
```
