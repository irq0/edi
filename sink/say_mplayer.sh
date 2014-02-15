#!/bin/bash

tmp=$(mktemp -t XXXXXX)
cat - > "$tmp"

mplayer "$tmp"

rm "$tmp"
