#!/usr/bin/env bash

# generate pylint statistics
pylint-3 --enable=all --disable=no-else-return,len-as-condition,locally-disabled,suppressed-message \
    ./kentauros ./scripts/ktr > meta/pylint_stats.txt
