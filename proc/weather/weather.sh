#!/bin/bash -x

GRAPHITE_HOST="mopp"
LOCATION="edlp"

subraum () {
    curl -s "http://${GRAPHITE_HOST}/render?target=sens.subraum.temp_1.degree_c&format=csv&from=-10min" \
	| awk '
BEGIN {
   FS=","
}
{
   printf "%.1f°C", $3
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
   printf "%.1f°C", temp
}'
}


echo "subraum: $(subraum) draußen: $(draussen)"
