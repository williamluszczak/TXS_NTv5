#!/usr/bin/env python

import numpy as np

def makejob(jobid, nsig, gamma):
    jobstr = """JOB {0} tint.sub 
VARS {0} inputseed=\"{0}\" nsig=\"{1}\" gamma=\"{2:.2f}\"""".format(jobid, nsig, gamma)
    return jobstr

i = 0
for nsig in np.arange(5.0, 100.0, 5.0):
    for gamma in np.arange(2.0,3.5,0.2):
        job = makejob(i, nsig, gamma)
        print(job)
        i+=1

