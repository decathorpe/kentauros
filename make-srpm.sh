#!/usr/bin/bash

NAME=kentauros
VERSION=0.9.2

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

