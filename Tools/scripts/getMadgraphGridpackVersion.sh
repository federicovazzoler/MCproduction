#!/bin/bash

gridpack=$(edmProvDump $1 | grep -o "'/cvmfs.*\.tar.*'")

echo "Gridpack is $gridpack"

dir="./mgbasedir/VERSION"
tar xf ${gridpack:1:-1} $dir
echo "Version info for gridpack"
head -n2 $dir
rm $dir
