#!/usr/bin/env bash

# create new sphinx-napoleon things
rm ./docs/source/apidoc/*
sphinx-apidoc-3 -f -o ./docs/source/apidoc/ ./kentauros

pushd docs
make clean
make html
popd
