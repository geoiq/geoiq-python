#!/bin/sh

# quick'n'dirty script to develop w/o system install stuff.
# . dev.sh

mkdir -p scratch
if [ ! -e scratch/venv-geoiq ]; then
    ant venv
fi

OLD_PS1="$PS1"
. scratch/venv-geoiq/bin/activate
PS1="\[\033[0;32m\] (geoiq) \[\033[0m\] $OLD_PS1"