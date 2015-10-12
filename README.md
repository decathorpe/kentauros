# kentauros

kentauros is a small, automatable (e.g. systemd timers) build script.

#### the following actions are supported at the moment:

- get sources from specified location (URL, git, bzr supported)
- build source packages from sources (only .src.rpm supported yet)
- upload source packages to cloud build services (only copr supported yet)

#### on my TODO-list:

- build source packages locally using mock
- verify that every needed bit of information is in the config file
- bump all package versions (in list of pkgs) except one (e.g. for soname bump)

