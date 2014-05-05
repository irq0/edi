#!/bin/bash

IFS="." read -r rc level action

export SUBINIT_LEVEL="$level"
export SUBINIT_ACTION="$action"
export EDI_METADATA="{\"runlevel\":\"${level}\",\"action\":\"${action}\"}"

echo "[x] RUNLEVEL ${level} ${action}"

(
	cd $(dirname $0)/../
	export PATH="./bin/:$PATH"
	run-parts --verbose --arg="$action" "rc${level}.d"
)
