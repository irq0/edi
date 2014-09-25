#!/bin/bash
gpio -g write 18 1
sleep .3
gpio -g write 18 0
