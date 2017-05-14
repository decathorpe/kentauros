#!/usr/bin/env bash

# generate pylint statistics
pylint-3 --enable=all -f html ./kentauros ./scripts/ktr > meta/pylint_stats.html
