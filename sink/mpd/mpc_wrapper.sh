#!/bin/bash

SCRIPTPATH="$(dirname $0)"
export MPC="mpc -q"
export MPD_HOST=${MPD_HOST:=localhost}


m () {
    echo "MPC: $MPC ${@}" >&2
    $MPC ${@}
}

read -r cmd arg
echo "CMD: $cmd $arg" >&2

if [[ $cmd =~ ^(volume|next|prev|toggle)$ ]]; then
    m "${cmd}"
elif [[ $cmd =~ ^(\+\+|\-\-|liquid|bassdrive)$ ]]; then
    case "${cmd}" in
	"++")
	    m volum +5
	    ;;
	"--")
	    m volum -5
	    ;;
	"bassdrive")
	    m clear
	    m insert "$(curl -s http://www.bassdrive.com/v2/streams/BassDrive3.pls | awk '/http/ { FS="="; $0=$0; print $2 }')"
	    m next
	    ;;
	"liquid")
	    m clear
	    ${SCRIPTPATH}/ldnb_mixes.py | while read -r line; do
		    m insert "$line"
	    done
	    m next
	    m shuffle
	    m play 1
	    ;;
    esac
elif [[ $cmd =~ ^(play)$ ]]; then
    m clear
    m insert "${arg}"
    m play 1
fi
