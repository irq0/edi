#!/bin/bash

readonly TMPDIR="$(mktemp -dt "tts.XXXXXXXXXX")"
readonly ERRLOG="$TMPDIR/err.log"

trap cleanup EXIT

tts() {
    local lang="$1"
    local msg="${@:2}"

    local id="$RANDOM"
    local wav="$TMPDIR/pico2wave_${id}.wav"
    local ogg="$TMPDIR/pico2wave_${id}.ogg"

    if pico2wave --lang="$lang" --wave="$wav" "$msg"; then
	oggenc -o "$ogg"  "$wav"
	echo "$ogg"
    else
	echo "pico2wave error :("
	exit 1
    fi
}

cleanup() {
    rm -rf "${TMPDIR}"
}

usage() {
    echo "USAGE: <--help | --text TEXT> [--lang de]"
    exit 1
}

cli() {
    local PARSED=$(getopt --name tts-pico2wave --options "h" --longoptions "help,voice:,lang:" -- "$@" 2> "$ERRLOG")

    err=$(cat $ERRLOG)

    if [[  -n $err ]]; then
	echo $err
	exit 1
    fi

    eval set -- "$PARSED"

    local lang="de-DE"
    local text=""

    while true; do
	case "$1" in
	    -h|--help)
		usage
		;;
	    --lang)
		if [[ -n $2 ]]; then
		    lang="$2"
		fi
		shift 2
		;;
	    --voice)
		shift 2
		;;
	    --)
		text="${@:2}"
		break
		;;
	esac
    done

    if [[ -z $lang || -z $text ]]; then
	echo "Error in commandline"
	exit 1
    else
	echo "$lang" "$text"
	exit 0
    fi
}
