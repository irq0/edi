#!/bin/bash

readonly LOCATION="edlp"

subraum () {
    curl -s "http://${GRAPHITE_SERVER:-localhost}/render?target=summarize(sens.subraum.temp_1.degree_c,\"10min\",\"avg\")&format=raw&from=-10min" \
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
    weather --metric "$LOCATION" \
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
echo "subraum: ${sub:-NA}°C draußen: ${dra:-NA}°C"
