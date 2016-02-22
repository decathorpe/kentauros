# TODO items for kentauros

- do not use --define for rpmbuild and mock,
  write to .spec file in temp. rpmbuild/SPECS directory instead

- ```package.__init__()```: make sure no hyphen is in source/version

- mock: use lockfile for waiting for running builds to finish?

- allow variables in package.conf and substitute
 - ```$(VERSION)```, ```$(NAME)```, etc.

- get release number from spec file (so --force is not necessary for packaging changes)

