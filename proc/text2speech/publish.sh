#!/bin/bash

tts() {
    msg=$(cat -)

    lang="$(echo "$msg" | ./langid -l "en,de,es" | awk '/de/ { print "de-DE" } /en/ { print "en-GB" } /es/ { print "es-ES" } ')"
    tmpdir="$(mktemp -dt "tts.XXXXXXXXXX")"
    tmp="$tmpdir/pico2wave.wav"
    pico2wave -l"$lang" -w"$tmp" "$msg"
    oggenc -o - "$tmp"
    rm -rf -- "$tmpdir"
}


publish() {
    amqp-publish \
	--url="amqp://localhost" \
	--exchange="notify" \
	--routing-key="audio" \
	--content-type="audio/vorbis"
}

tts | publish
