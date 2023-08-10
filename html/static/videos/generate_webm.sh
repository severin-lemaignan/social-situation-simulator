#!/bin/bash

for FILE in *.mp4 ; do
    OUTNAME=`basename "$FILE" .mp4`.webm
    ffmpeg -i $FILE -c:v libvpx -b:v 1M -c:a libvorbis $OUTNAME
done
