#!/usr/bin/env bash

# generate pylint statistics
python3-pylint --enable=all -f html ./kentauros ./scripts/ktr > meta/pylint_stats.html
