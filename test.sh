#!/usr/bin/env bash

./ktr.py -d clean -a

git checkout -- examples/state.json

./ktr.py -d chain -a

git checkout -- examples/specs

./ktr.py -d clean -a

git checkout -- examples/state.json
git checkout -- examples/specs

rm -f examples/specs/*.old
