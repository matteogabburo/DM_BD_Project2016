#!/bin/sh

COUNTER=0
conf_folder=$1
out_folder=$2

if [ ! -d "$out_folder" ]; then
	mkdir "$out_folder"
fi

for entry in "$conf_folder"/*
do
	let COUNTER=COUNTER+1
	echo "TEST N : $COUNTER, conf file : $entry =================================="
	python processing.py "$entry" "$out_folder"
	echo "========================================================================"
done

echo "__FINISH__"
