#!/bin/bash

# To update PATH environment variable to hold path
# for power-advanced-toolchain.
# By default power advance tool chain is installed
# at /opt/atX.X

# Regular expression to match directory names such as at8.0,at9.0..,atX.X
regex=^at[0-9]*.[0-9]*$
version=0.0
cd /opt

# Looping over all the directories in /opt folder to find a match for
# power-advance-toolchain directory. In case multiple versions are present
# such as atX.X and atY.Y (where Y.Y > X.X) we prepend the latest version
# to the PATH variable.

for dir in *
do
  if [[ -d ${dir} && $dir =~ $regex ]]; then
    echo $dir
    temp=$(echo "${dir:2} > $version" | bc)
    if [[ $temp -gt "0" ]]; then
        version=${dir:2}
    fi
  fi
done

if [ $version != "0.0" ]; then
  export PATH=/opt/at$version/bin:$PATH
fi
cd ~
