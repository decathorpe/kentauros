#!/usr/bin/bash

# generate pylint statistics
python3-pylint --enable=all -f html ./ktr ./ktr-config ./ktr-create ./kentauros > meta/pylint_stats.html

