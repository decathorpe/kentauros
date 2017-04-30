#!/usr/bin/env bash

NAME=kentauros
VERSION=$(python3 -c 'from kentauros.definitions import KTR_VERSION; print(KTR_VERSION, end="")')

mkdir -p $HOME/rpmbuild/SOURCES
mkdir -p $HOME/rpmbuild/SPECS

git archive --format=tar.gz --prefix=$NAME-$VERSION/ HEAD > $HOME/rpmbuild/SOURCES/$NAME-$VERSION.tar.gz

cp ./$NAME.spec $HOME/rpmbuild/SPECS/

cd $HOME/rpmbuild/SPECS/
rpmbuild -bs $NAME.spec
rm $NAME.spec

cd $HOME/rpmbuild/SOURCES/
rm $NAME*.tar.gz

cd $HOME/rpmbuild/SRPMS/
mv kentauros*.rpm $HOME/
