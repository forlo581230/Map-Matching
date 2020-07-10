#!/bin/bash

files="$@"

for i in $files;
do
    echo "Doing $i"
    java -jar ./matching-web/target/graphhopper-map-matching-web-1.0-SNAPSHOT.jar match $i
done

