#!/usr/bin/env bash

# generate pylint statistics
pylint-3 --enable=all ./kentauros ./scripts/ktr > meta/pylint_stats.txt
