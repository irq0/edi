#!/bin/bash -x

LOCATION="edlp"

subraum () {
    curl -s "http://${GRAPHITE_SERVER:-localhost}/render?target=summarize(sens.subraum.temp_1.degree_c,\"10min\",\"avg\")&format=raw&from=-10min" \
	| awk '
BEGIN {
   FS="|";
}
{
   FS=",";
   $0=$2;
   if ($2 == "None") {
      print "NA"
   } else {
      printf "%.1f°C", $2;
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
   printf "%.1f°C", temp
}'
}


echo "subraum: $(subraum) draußen: $(draussen)"
