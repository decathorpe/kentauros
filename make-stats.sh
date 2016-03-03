#!/usr/bin/bash

# generate pylint statistics
python3-pylint -f html ./ktr ./kentauros > stats/pylint_stats.html

cd ./stats

# generate cloc statistics
cloc --xml --xsl=1 --exclude-dir=../stats --exclude-dir=../examples \
    --exclude-ext=html,xml,xsl --out=./cloc.xml ../

