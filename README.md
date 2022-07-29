# TXS_NTv5 Cross Checks
Scripts for cross-checking the TXS 0506+056 untriggered flare analysis with the NorthernTracks v5 data sample (specifically NorthernTracks v005p001, though PointSourceTracks v002p03 and v003p02 are also used for comparison in the scripts included in this repository). 

Prerequisites:
You'll need to load a py3-v4.1.1 cvmfs environment:
```
eval `/cvmfs/icecube.opensciencegrid.org/py3-v4.1.1/setup.sh`
```

You will additionally need [the generic PDF ratio branch](https://github.com/icecube/csky/tree/feature/generic-pdf-ratio) of csky, which will (soon) be merged into `main` for csky version 1.1.10 (I'll update this readme when that happens)

## Fit Bias Checks

The first step in reproducing the fit bias plots is to run the included `generate_fitbias_data_tint.py` in the `Notebooks` directory:

```
python Notebooks/generate_fitbias_data_tint.py
```

This will create trials that are used for the time-integrated fit bias checks. This script takes several hours to run, so it's best to run it in the background while working on something else. 

Once both this script has finished running, your `Notebook` directory should have a whole bunch of new `.npy` files and you should be able to run the included `Notebooks/FitBias.ipynb` notebook to reproduce the relevant plots. Note that for the time dependent fits this notebook makes use of pre-generated trials that exist in `/data/user/wluszczak/KDE_csky/reproducibility/`. If you wish, you can generate your own version of these trials using the cluster and the provided scripts. The following script will create a dagman that can be submitted to the cluster to generate your own version of these trials:

```
python builddag_sens_ntv5.py $(outputdir) $(gamma) $(t0) $(dt) > my_fitbias_dagman.dag
```

Where:
- `$(outputdir)` is the directory you want outputfiles to be written to (ideally somewhere in your `/data/user/`)
- `$(gamma)` is the spectral index you want to simulate. To reproduce the fit bias plots I have show, set this to `2.0`
- `$(t0)` is the central time (MJD) of the flare being simulated. To reproduce my plots, set this to `57017.01`
- `$(dt)` is the flare duration. To reproduce my plots, set this to `10.0`

I've included an example dagman `Notebooks/sens_ntv5.dag` to give you an idea of what this should look like. You dagman should be exactly the same, but `$(outputdir)` should point to somewhere where you have write access (ideally somewhere on your `/data/user/`). 

Once you have the dagman assembled, you should be able to submit it from the submitter node as normal, provided that you have copied over the appropriate files to your submission directory (in this case, just the dagman and the submission script `time_dep.sub`):

```
condor_submit_dag my_fitbias_dagman.dag
```
Once you have these trials generated, you might need to modify the python notebook to use your files instead of mine. This can be done by simply changing the `trialfile_dir` variable in the first cell:

```
trialfile_dir = '$(outputdir)'
```

Where `$(outputdir)` is the directory you told the dagman to write your files to in the script calls above. 

## Sensitivity Comparison
To reproduce the sensitivity comparison plot, you will need to generate both background and injected signal trials for each data sample. To build dagmans that will generate background trials, use the included scripts:

```
python builddag_ntv5.py $(outputdir) 0 0 0 0 > my_ntv5_bg.dag
python builddag_psv2.py $(outputdir) 0 0 0 0 > my_psv2_bg.dag
python builddag_psv3.py $(outputdir) 0 0 0 0 > my_psv3_bg.dag
```

Where `$(outputdir)` is the place where you want output files to be written. You can additionally create dagmans for injected signal trials with:

```
python builddag_sens_psv2.py $(outputdir) $(gamma) $(t0) $(dt) > my_psv2_sig.dag
python builddag_sens_psv3.py $(outputdir) $(gamma) $(t0) $(dt) > my_psv3_sig.dag
python builddag_sens_ntv5.py $(outputdir) $(gamma) $(t0) $(dt) > my_ntv5_sig.dag
```

Where:
- `$(gamma)` is the spectral index you want your trials to have. To reproduce my plots, set this to `2.2`
- `$(t0)` is the central time at which flares are injected. To reproduce my plots, set this to `57017.01`
- `$(dt)` is the injected flare duration. To reproduce my plots, set this to `158.0`

Submit these dagmans to the cluster as normal (ensure that the *.sub submit files are also in the same directory you're submitting from). Output files will be written to `$(outputdir)`. There will be multiple files for a single injected `ns` value, so you'll need to do a bit of file combination once all the jobs have finished running using the included script:

```
python combine_trialfiles.py $(globlist) $(outputfile)
```

This script will combine all the files that match a certain pattern (`$(globlist)`) into a single file (`$(outputfile)`). `$(globlist)` is a Unix style pathname, e.g. to combine all the NTv5 files with `ns=2.0`, you can run:

```
python combine_trialfiles.py $(outputdir)/ntv5_output_2.0_*_158.0_*.npy ntv5_sigtrials_2.0_ns.npy
```

Which will combine all the NTv5 trials with 2 injected signal events and a flare duration of 158.0 days that you created previously. In total, you'll need to combine files for each sample (NTv5, PSv2, and PSv3) and for each set of `ns`. In total, you'll be running something that looks like this:

```
for in {0.0,2.0,4.0,6.0,8.0,10.0,12.0,14.0,16.0,18.0,20.0}; do
  python combine_trialfiles.py $(outputdir)/ntv5_output_$i_*_158.0_*.npy ntv5_sigtrials_$i_ns.npy
done

for in {0.0,2.0,4.0,6.0,8.0,10.0,12.0,14.0,16.0,18.0,20.0}; do
  python combine_trialfiles.py $(outputdir)/psv3_output_$i_*_158.0_*.npy psv3_sigtrials_$i_ns.npy
done

for in {0.0,2.0,4.0,6.0,8.0,10.0,12.0,14.0,16.0,18.0,20.0}; do
  python combine_trialfiles.py $(outputdir)/psv2_output_$i_*_158.0_*.npy psv2_sigtrials_$i_ns.npy
done
```

Once all of this has been done, modify the first cell in `Notebooks/Sensitivity.py` to point `trialfile_dir` to the directory where you wrote your data files. You should then be able to run the included `Notebooks/Sensitivity.py` start to finish. 
