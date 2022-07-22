#!/usr/bin/env python

import numpy as np

def makejob(jobid, ns, gamma, t0, dt):
    jobstr = """JOB {0} time_dep.sub 
VARS {0} inputseed=\"{0}\" nevents=\"{1}\" gamma=\"{2}\" t0=\"{3}\" dt=\"{4}\"""".format(jobid, ns, gamma, t0, dt)
    return jobstr

jobid = 0
for ns in np.arange(2,20,2):
    gamma = 2.2
    t0 = 57017.01
    dt = 79
    for i in range(0,20):
        print(makejob(jobid, ns, gamma, t0, dt))
        jobid+=1
