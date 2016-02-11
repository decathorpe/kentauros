# TODO items for kentauros

- rpmbuild for src.rpms
 - change os.environ['HOME'] to KTRDIR/rpmbuild/PKGDIR

- mock for local builds
 - use lockfile for waiting for running builds to finish?

- allow variables in package.conf and substitute
 - $(VERSION), $(NAME), etc.

- make KTR_CONF a ConfigParser object directly
- revert PACKAGE_CONF to using ConfigParser directly

- add PACKAGE_CONF.verify() to verify configuration validity
- refactor to allow modularisation into plugins (less dependencies)

