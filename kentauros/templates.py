PACKAGE_CONF_TEMPLATE = """# This is a package.conf template.
#
# The expected type is given for all keys that are not normal strings, with
# default values in parentheses. All listed keys need to be specified, even if
# left empty (running 'ktr verify' checks your .conf file for errors).
#
# Lists are expected to be comma-separated (comma only, no spaces!).
# Quasi-enums are given in parantheses, separated by forward slashes (choose
# one).
#
# Examples for .conf files can be found in the "examples" folder of the
# kentauros sources.

[package]
name =
version =
release =
# supported modules: source, constructor, builder, uploader
modules =

# only specified modules are necessary
[modules]
#source = (git / url / local)
#constructor = (srpm)
#builder = (mock)
#uploader = (copr)

# only if source = git:
#[git]
#keep = bool()
#keep_repo = bool()
#orig =
#ref =
#shallow = bool()

# only if source = url:
#[url]
#keep = bool()
#orig =

# only if source = local:
#[local]
#keep = bool()
#orig =

# only if constructor = srpm:
#[srpm]

# only if builder = mock:
#[mock]
#active = bool()
#dists = list()
#export = bool()
#keep = bool()

# only if package/uploader=copr
#[copr]
#active = bool()
#dists = list()
#keep = bool()
#repo =
#wait = bool()
"""

KENTAUROSRC_TEMPLATE = """# default kentaurosrc file
[main]
basedir=./

version_template_git = %{version}%{version_sep}%{date}.%{time}.git%{shortcommit}

version_separator_pre = ~
version_separator_post = +
"""
