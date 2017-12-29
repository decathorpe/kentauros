# kentauros

[![Documentation Status](https://readthedocs.org/projects/kentauros/badge/?version=stable)](http://kentauros.readthedocs.io/en/stable/?badge=stable)
[![Documentation Status](https://readthedocs.org/projects/kentauros/badge/?version=latest)](http://kentauros.readthedocs.io/en/latest/?badge=latest)


kentauros is a small, automatable (e.g. systemd timers) build script.

## the following module types are defined:

- `source`: manipulate a package's sources
- `constructor`: manipulate / construct source packages
- `builder`: manipulate / build binary packages
- `uploader`: manipulate / upload source packages to cloud services
- `package`: manipulate packages as a whole
- `init`: initialize a kentauros project from default templates

## source support

At the moment, git repositories and local and remote tarballs are supported as sources for a
package. The following actions are supported for sources:

- `clean`: clean up source files / repositoires
- `get`: get (download / copy) source files / repositories
- `export`: export source repositories to tarballs
- `prepare`: get, update, export in one step
- `refresh`: clean up sources and get them again
- `status`: print status messages
- `update`: update repositories
- `verify`: verify configuration and assert that all required binaries are present

The `git` source module requires that the `GitPython` python3 module (`python3-GitPython` package on
fedora) and the `git` binary (`git` package on fedora) are available on the system. The `url` source
module requires the `wget` binary (`wget` package on fedora).

## constructor support

## builder support

## uploader support




# working with the code base (on fedora)

To be able to run test scripts and the provided `ktr.py` script, it is necessary
to install some package dependencies, for example on fedora:

- `copr-cli`
- `git`
- `mock`
- `python3-argcomplete`
- `python3-GitPython` (when using git sources)
- `python3-tinydb`
- `rpm-build`
- `rpmdevtools`
- `wget`

If you want to generate pylint stats or build the docs locally, you will also need:

- `python3-pylint` (for generating stats before commits: `./make-stats.sh`)
- `python3-sphinx` (for generating and building docs locally: `./make-docs.sh`)

You can install all dependencies with the following command:

```sh
sudo dnf install copr-cli git mock python3-argcomplete python3-GitPython python3-pylint python3-sphinx python3-tinydb rpm-build rpmdevtools wget
```
