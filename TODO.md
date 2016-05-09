# TODO items for kentauros


These TODO items complement those found within the code itself.


## ktr

- add exports directory to configuration / initialisation. built binary packages
  will be put there eventually


## actions/verify

- implementation missing


## builder/mock

- export successfully built RPM packages to `$EXPODIR`


## package

- at initialisation, replace hyphens in source/version with tilde
- allow variables in package configuration file (`$(VERSION)`, `$(NAME)`)


## source/bzr

- bzr lightweight checkouts are not supported yet


# final ktr docstring versions

- `__init__.py`
- `bootstrap.py`
- `conntest.py`
- `definitions.py`
- `instance.py`
- `package.py`

- `actions`
  - `acts.py`

- `build`
  - `__init__.py`
  - `builder.py`
  - `mock.py`

- `config`
  - `__init__.py`
  - `cli.py`
  - `common.py`
  - `envvar.py`
  - `fallback.py`

- `construct`
  - `__init__.py`
  - `constructor.py`
  - `srpm.py`
  - `rpm_spec.py`

- `init`
  - `__init__.py`
  - `cli.py`
  - `env.py`

- `run`
  - `__init__.py`
  - `common.py`
  - `ktr.py`
  - `ktr_config.py`
  - `ktr_create.py`

- `source`
  - `__init__.py`
  - `source.py -> common.py`
  - `bzr.py`
  - `local.py`
  - `url.py`

- `upload`
  - `__init__.py`
  - `uploader.py`
  - `copr.py`

