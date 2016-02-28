# kentauros

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
- change package configuration values by command line: ```config``` action

To test out ktr with the provided examples, run in the project base directory:

```sh
./ktr --basedir=./examples $ACTION --all
./ktr --basedir=./examples config --section=mock --key=active --value=True
```

## on my TODO-list:

- verify that every needed bit of information is in the config file: ```verify``` action (only skeleton implementation present)

