#!/bin/bash

IFS="." read -r rc level action

export PATH="$(dirname $0)/bin:$PATH"
export SUBINIT_LEVEL="$level"
export SUBINIT_ACTION="$action"

function echo-with-color-code
{
    reset='\e[00m'
    $ECHO -e "${1}${*:2}${reset}"
}

function echo-with-color
{
    declare -A color
    #colors
    color["red"]='\e[00;31m' # Red
    color["green"]='\e[00;32m' # Green
    color["yellow"]='\e[00;33m' # Yellow
    color["blue"]='\e[00;34m' # Blue
    color["purple"]='\e[00;35m' # Purple
    color["cyan"]='\e[00;36m' # Cyan
    color["white"]='\e[00;37m' # White

    echo-with-color-code ${color[$1]} ${*:2}
}

function info
{
    echo-with-color green $@
}

info "[x] RUNLEVEL ${level} ${action}"

run-parts --verbose --arg="$action" "rc${level}.d"
