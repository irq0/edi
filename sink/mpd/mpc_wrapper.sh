#!/bin/bash

SCRIPTPATH="$(dirname $0)"
export MPC="mpc"
export MPD_HOST=${MPD_HOST:=localhost}


m () {
    echo "MPC: $MPC ${@}" >&2
    $MPC ${@} | awk '!/^(\[|volume)/ { print $0 }'
}

notify () {
    text="$@"
    if [[ -n $text ]]; then
       emit_cmd tts --voice willbadguy --text "Playing: ${text}"
       emit_msg "Playing ${text}" # TODO use loev service!
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
      gsub(/:.*$/,"", title); 
      print title 
   } 
}'
}

read -r cmd arg
echo "CMD: $cmd $arg" >&2

if [[ $cmd =~ ^(volume|next|prev|toggle|insert|play|pause|stop|clear)$ ]]; then
    m "${cmd}" "${arg}"
elif [[ $cmd = "playthis" ]]; then
    m clear
    m insert "${arg}"
    sleep 2
    m play 
elif [[ $cmd = "playpls" ]]; then
    m clear

    for adr in $(curl -s "${arg}" | awk 'BEGIN { FS="=" } /File/ { print $2 }'); do
        m insert "${adr}"
    done
    sleep 2
    m play 
fi

sleep 2
notify "$(stat)"
