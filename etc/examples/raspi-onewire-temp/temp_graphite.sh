#!/bin/bash
echo "sens.subraum.temp_1.degree_c $(~/temp.sh) $(date -u '+%s')" | nc mopp 2003
