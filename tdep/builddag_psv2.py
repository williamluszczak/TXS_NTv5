#!/usr/bin/env python
import sys

outputdir = str(sys.argv[1])
ns = float(sys.argv[2])
gamma = float(sys.argv[3])
t0 = float(sys.argv[4])
dt = float(sys.argv[5])

def makejob(jobid, ns, gamma, t0, dt):
    jobstr = """JOB {0} time_dep_psv2.sub 
VARS {0} inputseed=\"{0}\" nevents=\"{1}\" gamma=\"{2}\" t0=\"{3}\" dt=\"{4}\" outputdir=\"{5}\"""".format(jobid, ns, gamma, t0, dt, outputdir)
    return jobstr

for i in range(0,500):
    print(makejob(i, ns, gamma, t0, dt))

