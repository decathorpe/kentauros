#!/usr/bin/bash

# generate pylint statistics
python3-pylint -f html ./ktr ./ktr-config ./kentauros > stats/pylint_stats.html

