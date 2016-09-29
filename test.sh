#!/usr/bin/env bash

set -e

./ktr.py -v clean -a
rm -f examples/state.json

./ktr.py -v chain -a

git checkout -- examples/specs

./ktr.py -v clean -a
rm -f examples/state.json

