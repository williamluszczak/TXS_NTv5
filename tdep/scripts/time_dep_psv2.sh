#!/bin/bash

eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/setup.sh`
python /home/wluszczak/KDE_csky/tdep/scripts/time_dep_psv2.py $1 $2 $3 $4 $5
