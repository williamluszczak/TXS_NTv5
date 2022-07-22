#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import sys
import csky as cy
import os
import photospline as psp
from csky import cext
import time
from csky import hyp
import copy

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

#        print("evaluating calc_sb_ratio over", len(log_psi), "events")

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

inputseed = int(sys.argv[1])
nsig = float(sys.argv[2])
gamma = float(sys.argv[3])

ana_dir = cy.utils.ensure_dir('/data/ana/analyses/')
ana = cy.get_analysis(cy.selections.repo, 'version-005-p00', cy.selections.NTDataSpecs.nt_v5[0:1], dir=ana_dir, min_sigma=0.0)

base_path='/data/user/hmniederhausen/point_sources/skyllh/v005p00/frankenstein/input/'

spatial_pdf = psp.SplineTable(os.path.join(base_path, 'sig_E_psi_photospline_v006_4D.fits'))
energy_pdf = psp.SplineTable(os.path.join(base_path, 'E_dec_photospline_v006_3D.fits'))
bkg_pdf = psp.SplineTable(os.path.join(base_path, 'bg_2d_photospline.fits'))

src_catalog = np.load('/home/wluszczak/KDE_csky/tdep/scripts/large_catalog.npy')
src_catalog = src_catalog[src_catalog['event']==50579430]

#srcs = cy.sources(src_catalog['ra'], src_catalog['dec'], name=src_catalog['event'])
srcs = cy.sources(np.radians(40.667), np.radians(-0.0069), name=0)

tr = cy.get_trial_runner(ana=ana, src=srcs, space='generic', func=calc_sb_ratio, features={'ev_ra':'ra', 'ev_dec':'dec', 'ev_angErr':'sigma', 'ev_logE':'log10energy'}, fits={'gamma':(1.0,2.0,3.0,4.0)}, extra_keep=['dec', 'sigma', 'sindec', 'event'], energy=False, cut_n_sigma=np.inf, concat_evs=True, flux=hyp.PowerLawFlux(gamma))

all_results = []

for i in range(0,1):
    print("trial", i)
    trial_results = {}
    trialseed = (inputseed*1000)+i
    trial = tr.get_one_trial(n_sig=nsig, TRUTH=True, seed=trialseed)
    for src in srcs:
        srcra = src['ra']
        srcdec = src['dec']
        srcname = src['name']
        src = cy.sources(srcra, srcdec, name=srcname)

        t1 = time.time()

        tr_src = cy.get_trial_runner(ana=ana, src=src, space='generic', func=calc_sb_ratio, features={'ev_ra':'ra', 'ev_dec':'dec', 'ev_angErr':'sigma', 'ev_logE':'log10energy'}, fits={'gamma':(1.0,2.0,3.0,4.0)}, extra_keep=['dec', 'sigma', 'sindec', 'event'], energy=False, cut_n_sigma=5., concat_evs=True, flux=hyp.PowerLawFlux(gamma))

    #    new_trial = copy.deepcopy(trial)
    #    for k in range(0,len(trial[0])):
    #        print("removing event", srcname)
    #        ev_mask = (trial[0][k][0].event == srcname)
    #        new_trial[0][k][0] = trial[0][k][0][~ev_mask]

        trial_mask = dist_mask(trial[0][0][0], src, 15.)
        fit = tr_src.get_one_fit_from_trial(trial,flat=False,_masks=[trial_mask], TRUTH=True)
        print(fit)
        t2 = time.time()
        print("fit took", t2-t1)
        ts = fit[0]
        gamma_fit = fit[1]['gamma']
        ns_fit = fit[1]['ns']
        trial_results[int(srcname)]=[ts, ns_fit, gamma_fit]
    all_results.append(trial_results)
    
all_results = np.array(all_results)
print(all_results)
print(len(all_results))
np.save('/data/user/wluszczak/KDE_csky/tint/tint_bg.npy', all_results)
#np.save('test_results.npy', all_results)
#if nsig==0.:
#    np.save('/data/user/wluszczak/KDE_csky/tint/bg/tint_bg_%s.npy'%(inputseed), all_results)
#else:
#    np.save('/data/user/wluszczak/KDE_csky/tint/ns/tint_%s_%s.npy'%(nsig, inputseed), all_results)

#if nsig==0.:
#    np.save('/data/user/wluszczak/KDE_csky/tint/bg/tint_bg_%s.npy'%(inputseed), results)
#else:
#    np.save('/data/user/wluszczak/KDE_csky/tint/ns/tint_%s_%s_%s.npy'%(nsig, gamma,inputseed), results)
