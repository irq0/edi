#!/bin/bash

# EDI weather app
#
# Author: Marcel Lauhoff <ml@irq0.org>

graphite () {
    curl -s "http://${GRAPHITE_SERVER:-localhost}/render?target=summarize(${WEATHER_GRAPHITE_METRIC},\"10min\",\"avg\")&format=raw&from=-10min" \
	| awk '
BEGIN {
   FS="|";
}
{
   FS=",";
   $0=$2;
   if ($2 != "None") {
      printf "%.1f", $2;
   }
   exit 0;
}'
}

draussen () {
    weather --metric "$WEATHER_LOCATION" \
	| awk '
BEGIN {
   FS=":"
}
/Temperature/ {
   temp=$2
}
END {
   printf "%.1f", temp
}'
}

readonly sub="$(subraum)"
readonly dra="$(draussen)"

echo "{\"subraum\":${sub:-null}, \"draussen\":${dra:-null}}" > /dev/fd/"${EDI_DATA_FD}"
echo "${WEATHER_LOCAL_NAME}: ${sub:-NA}°C draußen: ${dra:-NA}°C"
