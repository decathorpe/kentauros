#!/usr/bin/env bash

set -e

./ktr -v clean -a
rm -f examples/state.json

./ktr -v chain -a

git checkout -- examples/specs

./ktr -v clean -a
rm -f examples/state.json

