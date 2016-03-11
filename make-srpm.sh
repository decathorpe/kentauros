#!/usr/bin/bash

NAME=kentauros
VERSION=$(python3 -c 'from kentauros.definitions import KTR_VERSION; print(KTR_VERSION, end="")')

mkdir -p $HOME/rpmbuild/SOURCES
mkdir -p $HOME/rpmbuild/SPECS

git archive --format=tar.gz --prefix=$NAME-$VERSION/ HEAD > $HOME/rpmbuild/SOURCES/$VERSION.tar.gz

cp ./$NAME.spec $HOME/rpmbuild/SPECS/

cd $HOME/rpmbuild/SPECS/
rpmbuild -bs $NAME.spec

cd $HOME/rpmbuild/SRPMS/
mv *.rpm $HOME/

cd $HOME
rm -r rpmbuild

