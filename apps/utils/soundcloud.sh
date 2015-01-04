#!/bin/bash -x

url="$(cat -)"
media_url="$(youtube-dl -g "$url" | sed -e s/https/http/)"
title="$($(dirname $0)/soundcloud_title.py "$url")"

emit_cmd mpd playcont "$media_url"

if [[ -n $title ]]; then
    emit_cmd tts --voice willbadguy "Playing from soundcloud: ${title}"
fi
