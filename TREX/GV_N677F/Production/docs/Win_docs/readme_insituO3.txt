TITLE:  GV in situ O3

AUTHORS: 
Pollack, I.B.; Montzka, D.D.; Knapp, D.J.; Campos, T.L.; Weinheimer, A.J.
National Center for Atmospheric Research

PI Contact Info:  
1)wein@ucar.edu, 303-497-1444, NCAR, 3450 Mitchell Lane, Boulder, CO 80301
2)campos@ucar.edu, 303-497-1048, NCAR, 10802 Airport Court, Broomfield, CO 80021
3)ipollack@ucar.edu, 303-487-1413, NCAR, 3450 Mitchell Lane, Boulder, CO 80301

1.0DATA SET OVERVIEW

An ozone chemiluminescence instrument was flown onboard the NSF/NCAR GV aircraft, HIAPER, during the T-REX field campaign of Spring 2006.  Data from 12 research flights were recorded from 20060217 to 20060428.  This readme file corresponds to the final version of the O3 data, revision R1.

2.0INSTRUMENT DESCRIPTION

The operating principle of the O3 instrument is the measurement of chemiluminescence from the reaction of nitric oxide (NO) with ambient O3 using a dry-ice cooled red-sensitive photomultiplier employing photon counting electronics.  This O3 instrument has participated in numerous field campaigns prior to the T-REX project and is described in detail in previous publications [Ridley et al., 1992].  

The reagent NO (grade >99%) is supplied from a 500 psig lecture bottle purchased from Scott Specialty Gases.  Since NO is a toxic gas, the small high pressure cylinder, its regulator, and several safety features are contained inside a specially designed pressure safe vessel that is vented overboard the aircraft.  

Ambient air was sampled through a rear-facing inlet (outside the aircraft boundary layer).  The ambient air sample flow was controlled at 500 sccm, meanwhile the NO reagent was introduced to the reaction vessel in near-excess flow of ~ 2 sccm. Gas flows as well as the reaction vessel temperature (32 ± 0.1?C) and pressure (24 ± 0.05 torr) are all controlled at constant conditions resulting in maximum stability of the detected signal and instrument sensitivity.  

The instrument sensitivity (~1300 cps/ppbv) is determined from calibrations performed on the ground before and after each flight or set of back-to-back flights using a TECO model 49PS calibrator operated with high-quality ultra-pure air.  A near-linear calibration curve is generated in 100 ppb intervals from 0 to 1 ppm.  


3.0DATA COLLECTION AND PROCESSING

A 2nd order polynomial fit of the calibration curve provides a measure of the sensitivity of the instrument (represented by the linear term of the polynomial) as well as an expression with which to convert the raw count rate to a mixing ratio.  The TECO UV calibrator has an uncertainty of ± 2-3 ppbv, and successive calibrations provided sensitivities stable to within 3%.  Therefore, the overall uncertainty of the O3 instrument is ± (3 + 3% of the ambient measured mixing ratio) ppbv.  

The TECO 49PS calibrator has been recently checked over the full calibration range (0 to 1 ppm) against the ESRL/GMD Network Standard (Provided by Sam Oltmans of the NOAA ESRL Climate Monitoring & Diagnostics Laboratory).  Our calibrator reported a lower mixing ratio than the ESRL/GMD Network Standard by ~1% (ESRL/GMD Network Standard = 1.0084*our calibrator + 0.07).  The calibration of the ESRL/GMD Network Standard has been recently compared to the NIST standard within the past two years. The ESRL/GMD Network Standard reads about ~1% (NIST Standard = 1.011*ESRL/GMD Network Standard + 0.04) lower than the NIST standard.  The combined 2% correction has been applied to this dataset to agree with the NIST standard.  

The "raw" O3 mixing ratio is determined from fitting the PMT signal minus the "background" count rate to a 2nd order polynomial expression representative of the instrument sensitivity.  The background count rate from the detector is very close to the dark count rate of the PMT, which is sensitive to altitude due to secondary cosmic ray events.  [Ridley (1992)]  However, the background count rate did not exceed 300 cps, even at the highest altitude of 47 kft.  This background level is insignificant (less than 1%) of the signal count rate given the high level of sensitivity.  Thus only periodic measurements (once every 20 minutes or once every racetrack) of the background count rate need be made.  Background levels are determined throughout the flight by computer-controlled switching of a solenoid valve to flow high quality ultra-pure air to the instrument and out of the sampling inlet.  

The detector sensitivity can be affected by changes in ambient water vapor, as described by Ridley (1992, 1990). The "Raw" O3 data from each flight will be multiplied by (1 + 4.3 x 10-3[H2O]) where [H2O] is the mixing ratio of water vapor in the reaction vessel in parts per thousand by volume to correct for the effect of water vapor.  TDL water vapor measurements, simultaneously recorded on the same 1 Hz time scale, are used for the [H2O] term of this equation.  The correction will be insignificant for normal water vapor mixing ratios anticipated for the middle to upper troposphere and lower stratosphere where HIAPER racetracks for the T-REX project are concentrated.  However, the correction can be significant in continental boundary layer or warm marine areas, as is the case for some of the deep vertical soundings and for the inter-comparison flight (RF07, 20060406) with the UKMO FAAM-BAe146.

An additional correction for air sample lag time in the inlet tubing has been applied to the final O3 data.  Given a 9'4" length of ¼" Teflon tubing from the inlet to the air sample flow controller at the instrument, a time delay varying between 4 sec (near sea level) and 0.6 sec (at 47 kft) is applied to the O3 data based on inlet pressure measured just before the air sample flow controller.  

4.0DATA FORMAT

The O3 mixing ratio is reported in ppbv for all 12 research flights.  The O3 data has been merged with the RAF/GV data set.  

5.0DATA REMARKS

The O3 instrument recorded data for the full duration of each flight.  It was required to keep the reagent NO gas delivery system closed during take-off and landing for safety concerns.  Thus, a short selection of O3 data has been eliminated from the very beginning and end of each flight corresponding to times when there was no reagent NO gas flow.  Short sections of data points corresponding to times when the instrument was recording the "background" count rate are also eliminated from the final data, although this information has been incorporated into the final calibration.  Bad data points and zero modes are flagged as -32767 in all data sets.  The time vector is continuous with start and stop times (in UT sec) corresponding to those in the RAF GV aircraft data set.

Even though the ozone data is reported on a 1 Hz time scale, the inlet delay correction unevenly shifts the timescale of the O3 data.  For convenience of comparison with other aircraft data, the O3 data has been re-sampled to 1 second intervals adding an extra 0.1 s of timing uncertainty.  The time synchronization of the O3 data is currently good to <1 sec.  

A single point spike in the ozone data from 100 to 600 ppbv was observed near 81778.4 (in UT sec) during RF05 (20060325).  High rate ozone data (sampled at 10 Hz) shows multiple points over this peak suggesting that the signal arises from a real increase in O3 mixing ratio.  At the same time, a housekeeping signal (recorded at 1 Hz) from the inlet flow controller also reported a small change in flow rate.  However, this change (± 15 sccm out of 500 sccm) is not large enough to affect the sensitivity of the O3 instrument such that the resulting mixing ratio is likely to fall within the overall measurement uncertainty.

6.0REFERENCES

Ridley, B. A., and F. E. Grahek, A small, low flow, high sensitivity reaction vessel for NO chemilum-inescence detectors, J. Atmos. Oceanic Technol., 7, 307-311, 1990.
Ridley, B. A., F. E. Grahek, and J. G. Walega, A small, high-sensitivity, medium-response ozone detector for measurements from light aircraft, J. Atmos. Oceanic Technol., 9, 142-148, 1992.

