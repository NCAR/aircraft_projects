Instructions for re-processing:

Make sure you are looged in as nimbus in order to make production run.

Make sure Setup_rf?? files are set up to the desired processing rate
using option

pr=25

either activated or commented out. Once this is done, make sure that ../Lags
file is properly configured for the processing rate. Several GG* variables have
different lags for HRT vs LRT processing. These differences are pointed out in the Lags file.

Once this is done, you can run "run_all_csh" and it will produce all production files
and put them in /jnet/productiondata.

Note that RF10 and RF12 have wrong dates in the ADS file. They need to be
changed to 05/17/2006 and 05/22/2006 respectively. The script will do that but
make sure that the proper rate production file has correct dates.

This file was written by Pavel Romashkin
