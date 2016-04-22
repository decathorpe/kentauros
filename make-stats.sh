#!/usr/bin/bash

# generate pylint statistics
python3-pylint --enable=all -f html ./kentauros > meta/pylint_stats.html

