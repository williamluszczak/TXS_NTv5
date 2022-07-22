#!/usr/bin/env python

def makejob(jobid, ns, gamma, t0, dt):
    jobstr = """JOB {0} time_dep_psv3.sub 
VARS {0} inputseed=\"{0}\" nevents=\"{1}\" gamma=\"{2}\" t0=\"{3}\" dt=\"{4}\"""".format(jobid, ns, gamma, t0, dt)
    return jobstr

ns = 0
gamma = 2.2
t0 = 57017.01
dt = 79
for i in range(0,500):
    print(makejob(i, ns, gamma, t0, dt))

