#!/bin/bash

SRC=https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz

wget ffmpeg.txz $SRC -O
tar xvf ffmpeg.txz
mv ffmpeg-git-*/ffmpeg ./ffmpeg
rm -rf ffmpeg-git-* ffmpeg.txz
chmod a+x ./ffmpeg
