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
ana = cy.get_analysis(cy.selections.repo, 'version-003-p02', cy.selections.PSDataSpecs.ps_10yr_separate[-6:-3])


def GreatCircleDistance(ra_1, dec_1, ra_2, dec_2):
        '''Compute the great circle distance between two events'''
        '''All coordinates must be given in radians'''
        delta_dec = np.abs(dec_1 - dec_2)
        delta_ra = np.abs(ra_1 - ra_2)
        x = (np.sin(delta_dec / 2.))**2. + np.cos(dec_1) *\
            np.cos(dec_2) * (np.sin(delta_ra / 2.))**2.
        return 2. * np.arcsin(np.sqrt(x))

def spatial_kde(log_psi, log_ang_err, log_energy, gamma):
    return spatial_pdf.evaluate_simple([log_ang_err, log_energy, log_psi, np.full(len(log_psi), gamma)], 0)

def energy_kde(log_energy, src_dec, gamma):
    sin_src_dec = np.sin(src_dec)
    return energy_pdf.evaluate_simple([log_energy, np.full(len(log_energy), sin_src_dec), np.full(len(log_energy), gamma)], 0)

def calc_sb_ratio(ev_ra, ev_dec, ev_angErr, ev_logE, src, gamma, **kwargs):
    if '_mask' in kwargs:
        #print("there is a mask")
        mask = kwargs['_mask']
        antimask = mask[mask==False]
        src_ra = src['ra']
        src_dec = src['dec']

        ev_ra_mask = ev_ra[mask]
        ev_dec_mask = ev_dec[mask]
        ev_angErr_mask = ev_angErr[mask]
        ev_logE_mask = ev_logE[mask]
        
        psi = GreatCircleDistance(ev_ra_mask, ev_dec_mask, src_ra, src_dec)
        #cpsi = cext.get_dpsis_by_sigmas_for_space_pdf(ev_dec, ev_ra, ev_angErr, src_dec, src_ra, np.zeros(np.shape(src_ra)), 5.)

        log_psi = np.log10(psi)
        log_ang_err = np.log10(ev_angErr_mask)
        log_energy = ev_logE_mask
        masked_ev_dec = ev_dec_mask

        #print("evaluating calc_sb_ratio over", len(log_psi), "events")

        spdfs = spatial_kde(log_psi, log_ang_err, log_energy, gamma)
        spatial_norm = np.log(10) * psi * np.sin(psi)
        spdfs/= spatial_norm

        epdfs = energy_kde(log_energy, src_dec, gamma)

        bg_pdfs = bkg_pdf.evaluate_simple([log_energy, np.sin(masked_ev_dec)])
        sb_ratio_close = spdfs*epdfs/bg_pdfs

        far_evts_sb = np.zeros(len(antimask))
        #sb_ratio = np.concatenate([sb_ratio, far_evts_sb])
        sb_ratio = np.zeros(len(ev_ra))
        sb_ratio[mask] = sb_ratio_close
    
    else:
        src_ra = src['ra']
        src_dec = src['dec']
        psi = GreatCircleDistance(ev_ra, ev_dec, src_ra, src_dec)
        #cpsi = cext.get_dpsis_by_sigmas_for_space_pdf(ev_dec, ev_ra, ev_angErr, src_dec, src_ra, np.zeros(np.shape(src_ra)), 5.)

        log_psi = np.log10(psi)
        log_ang_err = np.log10(ev_angErr)
        log_energy = ev_logE
        masked_ev_dec = ev_dec

        #print("evaluating calc_sb_ratio over", len(log_psi), "events")

        spdfs = spatial_kde(log_psi, log_ang_err, log_energy, gamma)
        spatial_norm = np.log(10) * psi* np.sin(psi)
        spdfs/= spatial_norm

        epdfs = energy_kde(log_energy, src_dec, gamma)

        bg_pdfs = bkg_pdf.evaluate_simple([log_energy, np.sin(masked_ev_dec)])
        sb_ratio = spdfs*epdfs/bg_pdfs

        #far_evts_sb = np.zeros(len(antimask))
        #sb_ratio = np.concatenate([sb_ratio, far_evts_sb])
        
    return sb_ratio

def dist_mask(arr, src, cut_deg):
    out = np.zeros(len(arr), dtype=bool)
    ras = arr['ra']
    decs = arr['dec']
    psi = GreatCircleDistance(ras, decs, src.ra, src.dec)
    out = psi < np.radians(cut_deg)
    return out

def get_injflares(t0, twidth, nevts):
    nevts_actual = np.random.poisson(nevts)
    times = np.random.uniform(low=t0, high=t0+twidth, size=nevts_actual)
    injflares = [times, 0]
    return [injflares]

inputseed = int(sys.argv[1])
nevts = float(sys.argv[2])
gamma = float(sys.argv[3])
t0 = float(sys.argv[4])
dt = float(sys.argv[5])

#TXS best fit values

base_path='/data/user/hmniederhausen/point_sources/skyllh/v005p00/frankenstein/input/'

spatial_pdf = psp.SplineTable(os.path.join(base_path, 'sig_E_psi_photospline_v006_4D.fits'))
energy_pdf = psp.SplineTable(os.path.join(base_path, 'E_dec_photospline_v006_3D.fits'))
bkg_pdf = psp.SplineTable(os.path.join(base_path, 'bg_2d_photospline.fits'))

srcs = cy.sources(1.35049651, 0.09828762, name=50579430)
names = [50579430]
#srcfile = np.load('/home/wluszczak/KDE_csky/tdep/scripts/large_catalog.npy')
#srcfile = srcfile[srcfile['event']==50579430]
#ras = srcfile['ra']
##ras = np.random.uniform(0., 2.*np.pi, size=len(srcfile['ra']))
#decs = srcfile['dec']
#names = srcfile['event']
#print("loc", ras, decs)
#srcs = cy.sources(ras, decs, name=names)

#mtr = cy.conf.get_multiflare_trial_runner(ana=ana, src=srcs, threshold=100., space='generic', func=calc_sb_ratio,features={'ev_ra':'ra', 'ev_dec':'dec', 'ev_angErr':'sigma', 'ev_logE':'log10energy'}, fits={'gamma':(1.0,2.0,3.0,4.0)}, extra_keep=['dec', 'sigma', 'event'], energy=False, concat_evs=True, flux=hyp.PowerLawFlux(gamma), muonflag=True)
mtr = cy.conf.get_multiflare_trial_runner(ana=ana, src=srcs, threshold=100., extra_keep=['dec', 'sigma'])

all_fits = []
multiple_trials = []
for i in range(0,1):
    t1 = time.time()
    trialseed = (inputseed*100)+i
    if nevts!=0.:
        injflares = get_injflares(t0, dt, nevts)
        print("injflares is", injflares)
        mtr_trial = mtr.get_one_trial(seed=trialseed, injflares=injflares, TRUTH=False)
    else:
        mtr_trial = mtr.get_one_trial(seed=trialseed, TRUTH=True)

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
    np.save('/data/user/wluszczak/KDE_csky/sigtrials/psv3/psv3_%s_%s_%s_%s_%s.npy'%(nevts, gamma, t0, dt, inputseed), multiple_trials)

else:
#    np.save('/data/user/wluszczak/KDE_csky/tdep/bg/txs_bg_flares_%s.npy'%(inputseed), multiple_trials)
    np.save('/data/user/wluszczak/KDE_csky/bgtrials/psv3/psv3_bg_flares_%s.npy'%(inputseed), multiple_trials)
