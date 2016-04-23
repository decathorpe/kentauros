# TODO items for kentauros


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
- `conntest.py`
- `definitions.py`

- `actions`
  - `__init__.py`
  - `action.py`
  - `std_actions.py`
  - `config_action.py`
  - `create_action.py`

- `bootstrap`
  - `__init__.py`

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

- `instance`
  - `__init__.py`

- `package`
  - `__init__.py`

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

