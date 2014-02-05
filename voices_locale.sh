#!/bin/bash
$(dirname $0)/voices.py | \
awk 'BEGIN {
   FS=":";
   OFS=":"
}
/German/ {
   print "de_DE", $2
}
/English \(USA\)/ {
   print "en_US", $2
}
/English \(UK\)/ {
   print "en_GB", $2
}
'
