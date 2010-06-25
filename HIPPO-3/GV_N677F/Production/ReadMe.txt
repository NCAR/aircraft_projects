The processing for HIPPO-3 involves filling in gaps in position data caused by several ADS system crashes.
The position information is needed by other instruments that logged their data independently but rely upon
ADS to tie timing and location information.

In order to produce position data for the gaps, 3D position of the GV was extracted from the .nc files into
ASCII, linearly interpolated to extend level and sloping parts of the vertical profile and data were replaced
back into .nc files.

Interpolated data are included in Position_interpolation directory. Flights 03, 04, 06 and 10 are affected.

Contact Pavel with questions regarding this process.
pavel@ucar.edu
