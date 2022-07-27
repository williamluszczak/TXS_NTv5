#!/usr/bin/env python
import sys
import numpy as np

outputdir = str(sys.argv[1])
gamma = float(sys.argv[2])
t0 = float(sys.argv[3])
dt = float(sys.argv[4])

def makejob(jobid, ns, gamma, t0, dt):
    jobstr = """JOB {0} time_dep.sub 
VARS {0} inputseed=\"{0}\" nevents=\"{1}\" gamma=\"{2}\" t0=\"{3}\" dt=\"{4}\" outputdir=\"{5}\"""".format(jobid, ns, gamma, t0, dt, outputdir)
    return jobstr

jobid = 0
for ns in np.arange(2.0,20.0,2.0):
    for i in range(0,10):
        print(makejob(jobid, ns, gamma, t0, dt))
        jobid+=1
