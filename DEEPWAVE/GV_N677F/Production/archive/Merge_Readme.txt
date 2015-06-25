NOTE: BEFORE YOU ARCHIVE THE PRODUCTION DATA, COMFIRM MERGES WERE PERFORMED!

Production data are created by the RAF PMs using NIMBUS. Final output files
(both LRT and HRT) can be found in /scr/raf/local_productiondata - either in
that dir or in a subdir called DEEPWAVE. Check file dates to be sure you have
the latest data, and confirm with PMs if there are questions.

---------------------------------------
Merge instructions for DEEPWAVE project
---------------------------------------

Merge datasets are:
1) DGPS (Pavel, NCAR)
2) Terrain Hts calculated using an R script
3) Corrections to Pitch using an R script

All source data for merge are located in this directory.

TO MERGE DATASETS INTO LRT[HRT] FILES:
---------------------------------
[Command changes to process the HRT are given in square brackets.]

### check that files are reordered
> foreach file (`ls *.nc`)
foreach? ncdump -h $file | grep "Time =" | grep -v ResponseTime
foreach? end

### Merge DGPS and fix DGPS attributes
1) The 5 Hz DGPS files should be averaged to the middle of the second for the 1 Hz LRT merge. 
  - cd MERGE/DGPS
  - ncav -r 1 -b <batchfile>

2) Merge DGPS data files. These are located in /scr/raf/pavel/deepwave and are in netCDF format already.  For the flights that don't have the DGPS files empty variables are added to the final files to keep the variable count the same.

 /net/jlocal/projects/DEEPWAVE/GV_N677F/scripts/merge_dgps[_h].sh

Check against previous version to make sure did everything.

> foreach file ( `ls *nc` )
foreach? echo $file
foreach? ncdump -h $file | grep "_DGPS"
foreach? end

### Blank out calculated _gp vars based on criteria in file.
Criteria were developed by Al Cooper. See his writeup:
	xxx

3) Blanking needs to be applied to the production files. The criteria and
affected variables are:

> foreach file (`ls *[h.]nc`)
foreach?  /net/jlocal/projects/DEEPWAVE/GV_N677F/scripts/blankout_gp.pl $file
foreach? end

### Merge Terrain Ht vars (LRT only)
- code is /h/eol/janine/Rstudio/HeightOfTerrain/HeightOfTerrainNOMADSS.Rnw
- must be run on Tikal
edit to fix lat/lon per project, and run 
> AddHtTerrain DEEPWAVE

### Do ShulerOscillation correction
- code is /h/eol/janine/Rstudio/ShulerStudy/PitchCorrection.R
- must be run on Tikal
run
>CorrectPitch[H] DEEPWAVE

If this is the original release, when all the changes are made, rename the files to remove the Z, and PC from the names. For DEEPWAVE, I left the ZPC to avoid confusion with previous releases.

