#!/usr/bin/env python


import numpy as np
import glob
import sys

globarg = str(sys.argv[1])
outputname = str(sys.argv[2])

sigfiles = glob.glob(globarg)

all_results = []
i=0
for f in sigfiles:
    i+=1
    data = np.load(f, allow_pickle=True)
    for trial in data:
        all_results.append(trial[50579430])

all_results = np.array(all_results)
print(all_results)

np.save(outputname, all_results)
