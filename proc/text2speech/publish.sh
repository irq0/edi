#!/bin/bash

source "$(dirname $0)/SETTINGS"

tts() {
    msg=$(cat -)

    lang="$(echo "$msg" | langid -l "en,de" | awk '/de/ { print "de-DE" } /en/ { print "en-GB" }')"
    tmpdir="$(mktemp -dt "tts.XXXXXXXXXX")"
    tmp="$tmpdir/pico2wave.wav"
    pico2wave -l"$lang" -w"$tmp" "$msg"
    oggenc -o - "$tmp"
    rm -rf -- "$tmpdir"
}


publish() {
    amqp-publish \
	--url=$URL \
	--routing-key=$PUBLISH_QUEUE \
	--content-type="audio/vorbis"
}

tts | publish
