#!/bin/bash
set -x
./look.py $1 --plugins=unpack,$2 --nevents=-1 --output-file=output/run$1-$2.root
#./oneRun.py --file1=$1 --feds1=1776 --nevents=-1 --plugins=unpack,$2 --output-file=output/$2-$1 --progress 

