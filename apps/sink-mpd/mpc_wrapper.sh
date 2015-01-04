#!/bin/bash

# EDI MPD Sink
# Author: Marcel Lauhoff <ml@irq0.org>

SCRIPTPATH="$(dirname $0)"
export MPC="mpc"

m () {
    echo "MPC: $MPC ${@}" >&2
    $MPC ${@} | awk '!/^(\[|volume)/ { print $0 }'
}

notify () {
    text="$@"
    if [[ -n $text && ! ^http ]]; then
       emit_cmd tts --voice willbadguy "Playing: ${text}"
       emit_msg_action "turns on the radio: ${text}" # TODO use loev service!
    fi
}

stat () {
    mpc 2> /dev/null \
      | gawk '
!/^(\[|volume)/ {
   title=$0
}
/^\[/ {
   status=$1
}
END {
   if (status == "[playing]") {
      gsub(/(:|\[).*$/,"", title);
      print title
   }
}'
}

read -r cmd arg
echo "CMD: $cmd $arg" >&2

if [[ $cmd =~ ^(next|toggle|play)$ ]]; then
    m "${cmd}" "${arg}"
    m repeat yes
    notify "$(stat)"
elif [[ $cmd = "playthis" ]]; then
    m clear
    m insert "${arg}"
    sleep 2
    m play
    m repeat yes
    notify "$(stat)"
elif [[ $cmd = "playcont" ]]; then
    m insert "${arg}"
    sleep 2
    m next
    m repeat yes
    notify "$(stat)"
elif [[ $cmd = "playpls" ]]; then
    m clear

    for adr in $(curl -s "${arg}" | awk 'BEGIN { FS="=" } /File/ { print $2 }'); do
        m insert "${adr}"
    done
    sleep 2
    m play
    m repeat yes
    notify "$(stat)"
else
    m "${cmd}" "${arg}"
fi
