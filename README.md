# TXS_NTv5 Cross Checks
Scripts for cross-checking the TXS 0506+056 untriggered flare analysis with NTv5

## Fit Bias Checks

The first step in reproducing the fit bias plots is to run the included `generate_fitbias_data_tint.py` in the `Notebooks` directory. This will create trials that are used for the time-integrated fit bias checks. This script takes several hours to run, so it's best to run it in the background while working on something else. 

Once both this script has finished running, you should be able to run the included `Notebooks/FitBias.ipynb` notebook to reproduce the relevant plots. Note that for the time dependent fits this notebook makes use of pre-generated trials that exist in `/data/user/wluszczak/KDE_csky/reproducibility/`. If you wish, you can generate your own version of these trials using the cluster and the provided scripts. The following script will create a dagman that can be submitted to the cluster to generate your own version of these trials:

```
python builddag_sens_ntv5.py $(outputdir) $(gamma) $(t0) $(dt) > my_fitbias_dagman.dag
```

Where:
- `$(outputdir)` is the directory you want outputfiles to be written to (ideally somewhere in your `/data/user/`)
- `$(gamma)` is the spectral index you want to simulate. To reproduce the fit bias plots I have show, set this to `2.0`
- `$(t0) is the central time (MJD) of the flare being simulated. To reproduce my plots, set this to `57017.01`
- `$(dt) is the flare duration. To reproduce my plots, set this to `10.0`

I've included an example dagman `Notebooks/sens_ntv5.dag` to give you an idea of what this should look like. You dagman should be exactly the same, but `$(outputdir)` should point to somewhere where you have write access (ideally somewhere on your `/data/user/`). 

Once you have the dagman assembled, you should be able to submit it from the submitter node as normal, provided that you have copied over the appropriate files to your submission directory (in this case, just the dagman and the submission script `time_dep.sub`):

```
condor_submit_dag my_fitbias_dagman.dag
```
Once you have these trials generated, you might need to modify the python notebook to use your files instead of mine. This can be done by simply changing the `trialfile_dir` variable in the first cell:

```
trialfile_dir = '$(directory where you told the dagman to write your files)'
```
