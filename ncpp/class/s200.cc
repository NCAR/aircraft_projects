/*
-------------------------------------------------------------------------
OBJECT NAME:	s200.cc

FULL NAME:	DMT ASAS/PCASP

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2001
-------------------------------------------------------------------------
*/

#include "s200.h"


/* -------------------------------------------------------------------- */
S200::S200(NcFile *file, NcVar *av) : Probe(file, av)
{
  concIdx = dispIdx = dbarIdx = volIdx = -1;

  for (int i = 0; i < nOtherVars(); ++i)
    {
    if (strncmp(otherVars[i]->name(), "PACT", 4) == 0)
      actIdx = i;

    if (strncmp(otherVars[i]->name(), "PFLWC", 5) == 0)
      flowIdx = i;


    if (strncmp(otherVars[i]->name(), "CONCP", 5) == 0)
      concIdx = i;

    if (strncmp(otherVars[i]->name(), "DISPP", 5) == 0)
      dispIdx = i;

    if (strncmp(otherVars[i]->name(), "DBARP", 5) == 0)
      dbarIdx = i;

    if (strncmp(otherVars[i]->name(), "PVOLP", 5) == 0)
      volIdx = i;
    }

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void S200::ComputeConcentration(float *accum, float *conc, long countV[],
	float *otherVarData[])
{
  int		i, bin;
  float		*dia, *counts, *concentration;
  float		*flow, *activity;

  flow = otherVarData[flowIdx];
  activity = otherVarData[actIdx];

  for (i = 0; i < countV[0] * countV[1]; ++i)
    {
    counts = &accum[i * VectorLength()];
    concentration = &conc[i * VectorLength()];

    for (bin = FirstBin(); bin <= LastBin(); ++bin)
      sampleVolume[bin] = flow[i];

    dia = midPointDiam;

#define P_VOLUME

#include "pms1d_cv"

    otherVarData[concIdx][i] = totalConcen;
    otherVarData[dispIdx][i] = disp;
    otherVarData[dbarIdx][i] = dbar;

    if (volIdx >= 0)
      otherVarData[volIdx][i] = pvol;
    }

}	/* END COMPUTECONCENTRATION */

/* END S200.CC */
