/*
-------------------------------------------------------------------------
OBJECT NAME:	f300.cc

FULL NAME:	FSSP-300 Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1999
-------------------------------------------------------------------------
*/

#include "f300.h"


/* -------------------------------------------------------------------- */
F300::F300(NcFile *file, NcVar *av) : Probe(file, av)
{
  tasIdx = concIdx = dbarIdx = volIdx = -1;

  for (int i = 0; i < nOtherVars(); ++i)
    {
    if (strcmp(otherVars[i]->name(), "TASX") == 0)
      tasIdx = i;

    if (strncmp(otherVars[i]->name(), "CONC3", 5) == 0)
      concIdx = i;

    if (strncmp(otherVars[i]->name(), "DBAR3", 5) == 0)
      dbarIdx = i;

    if (strncmp(otherVars[i]->name(), "PVOL3", 5) == 0)
      volIdx = i;
    }

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void F300::ComputeConcentration(float *accum, float *conc, long countV[],
	float *otherVarData[])
{
  int	i, bin;
  float	*dia, *counts, *concentration, *tas;
  double vol;

  tas = otherVarData[tasIdx];
printf("f300: SampleArea needs to come from netCDF file.  Currently hardcoded 0.65.\n");
  for (i = 0; i < countV[0] * countV[1]; ++i)
    {
    counts = &accum[i * VectorLength()];
    concentration = &conc[i * VectorLength()];

    vol = tas[i] / dataRate * 0.065;    /* Sample Area taken from cal in 1994 */

    for (bin = FirstBin(); bin <= LastBin(); ++bin)
      sampleVolume[bin] = vol;

    dia = midPointDiam;

#define P_VOLUME

#include "pms1d_cv"

    otherVarData[concIdx][i] = totalConcen;
    otherVarData[dbarIdx][i] = dbar;

    if (volIdx >= 0)
      otherVarData[volIdx][i] = pvol;
    }

}	/* END COMPUTECONCENTRATION */

/* END F300.CC */
