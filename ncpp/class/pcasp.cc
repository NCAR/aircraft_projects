/*
-------------------------------------------------------------------------
OBJECT NAME:	pcasp.cc

FULL NAME:	ASAS/PCASP

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1999
-------------------------------------------------------------------------
*/

#include "pcasp.h"


/* -------------------------------------------------------------------- */
PCASP::PCASP(NcFile *file, NcVar *av) : Probe(file, av)
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
void PCASP::ComputeConcentration(float *accum, float *conc, long countV[],
	float *otherVarData[])
{
  int		i, bin;
  float		*dia, *counts, *concentration;
  float		*flow, *activity;
  double	vol;

  flow = otherVarData[flowIdx];
  activity = otherVarData[actIdx];

  for (i = 0; i < countV[0] * countV[1]; ++i)
    {
    counts = &accum[i * VectorLength()];
    concentration = &conc[i * VectorLength()];

    vol = (1.0 - activity[i] * dataRate) * (flow[i] / dataRate);
printf("vol=%f\n", vol);
    for (bin = FirstBin(); bin <= LastBin(); ++bin)
      sampleVolume[bin] = (float)vol;

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

/* END PCASP.CC */
