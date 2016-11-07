#!/usr/bin/env bash

# generate pylint statistics
python3-pylint --enable=all --jobs=4 -f html ./kentauros ./scripts/ktr > meta/pylint_stats.html
