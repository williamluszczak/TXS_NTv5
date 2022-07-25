#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import sys
import csky as cy
from csky import hyp
import time

import os
import photospline as psp


ana_dir = cy.utils.ensure_dir('/data/ana/analyses/')
#ana = cy.get_analysis(cy.selections.repo, 'version-005-p01', cy.selections.NTDataSpecs.nt_txs[0:1], dir=ana_dir, min_sigma=0.0)
ana_psv2 = cy.get_analysis(cy.selections.repo, 'version-002-p03', cy.selections.PSDataSpecs.ps_10yr_separate[-6:-3])

inputseed = int(sys.argv[1])
nevts = float(sys.argv[2])
gamma = float(sys.argv[3])
t0 = float(sys.argv[4])
dt = float(sys.argv[5])

#TXS best fit values

srcs = cy.sources(1.35049651, 0.09828762, name=50579430)
names = [50579430]

#mtr = cy.conf.get_multiflare_trial_runner(ana=ana, src=srcs, threshold=100., space='generic', func=calc_sb_ratio,features={'ev_ra':'ra', 'ev_dec':'dec', 'ev_angErr':'sigma', 'ev_logE':'log10energy'}, fits={'gamma':(1.0,2.0,3.0,4.0)}, extra_keep=['dec', 'sigma', 'event'], energy=False, concat_evs=True, flux=hyp.PowerLawFlux(gamma), muonflag=True)
mtr = cy.conf.get_multiflare_trial_runner(ana=ana, src=srcs, threshold=100., extra_keep=['dec', 'sigma'])

all_fits = []
multiple_trials = []
for i in range(0,10):
    t1 = time.time()
    trialseed = (inputseed*100)+i
    if nevts!=0.:
        injflares = get_injflares(t0, dt, nevts)
        print("injflares is", injflares)
        mtr_trial = mtr.get_one_trial(seed=trialseed, injflares=injflares, TRUTH=False)
    else:
        mtr_trial = mtr.get_one_trial(seed=trialseed, TRUTH=False)

#    new_trial = copy.deepcopy(mtr_trial)
#    for k in range(0,len(mtr_trial[0])):
#        print("removing event", srcname)
#        ev_mask = (mtr_trial[0][k][0].event in srcfile['event'])
#        new_trial[0][k][0] = mtr_trial[0][k][0][~ev_mask]


    mtr_fit = mtr.get_one_fit_from_trial(mtr_trial, flat=False, _fmin_epsilon=1e-3)
    print("mtr_fit is", mtr_fit)
#    print(mtr_fit.keys())
#    print(mtr_fit[list(mtr_fit.keys())[0]][-1])
    nice_output = {}
    for evt_id in names:
        flist = mtr_fit[evt_id][-1]
        if len(flist)!=0.:
            farr = np.empty(len(flist), dtype=[('tstart', float), ('tstop', float), ('ts', float), ('ns', float), ('gamma', float)])
            farr['tstart'] = flist.mjd_start
            farr['tstop'] = flist.mjd_end
            farr['ts'] = flist.ts
            farr['ns'] = flist.ns
            farr['gamma'] = flist.gamma
        else:
            farr = np.empty(1, dtype=[('tstart', float), ('tstop', float), ('ts', float), ('ns', float), ('gamma', float)])
            farr['tstart'] = [0.]
            farr['tstop'] = [0.]
            farr['ts'] = [0.]
            farr['ns'] = [0.]
            farr['gamma'] = [0.]
        nice_output[evt_id]=farr
    print(nice_output)
    t2 = time.time()
    print("time taken:", t2-t1)
    #all_fits.append(farr)
    multiple_trials.append(nice_output)
print(multiple_trials)

if nevts!=0.:
    np.save('/data/user/wluszczak/KDE_csky/tdep/sig/psv2_flares_%s_%s_%s_%s_%s.npy'%(nevts, gamma, t0, dt, inputseed), multiple_trials)
else:
    np.save('/data/user/wluszczak/KDE_csky/tdep/bg/psv2_bg_flares_%s.npy'%(inputseed), multiple_trials)
