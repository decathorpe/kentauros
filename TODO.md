# TODO items for kentauros

- ```package.__init__()```: make sure no hyphen is in source/version

- rpmbuild for src.rpms
 - change ```os.environ['HOME']``` to ```KTRDIR/rpmbuild/PKGDIR```

- mock for local builds
 - use lockfile for waiting for running builds to finish?

- allow variables in package.conf and substitute
 - ```$(VERSION)```, ```$(NAME)```, etc.

- get release number from spec file (so --force is not necessary for packaging changes)

