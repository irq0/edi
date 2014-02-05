#!/bin/sh

$(dirname $0)/voices.py  | awk 'BEGIN { FS=":"; ORS="," } { print tolower($2) }' > $(dirname $0)/default_voices