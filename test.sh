#!/usr/bin/env bash

set -e

rm -f examples/state.json

./ktr -v clean -a

./ktr -v chain -a

git checkout -- examples/specs

rm -f examples/state.json

./ktr -v clean -a
