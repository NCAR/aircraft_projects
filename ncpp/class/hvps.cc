/*
-------------------------------------------------------------------------
OBJECT NAME:	hvps.cc

FULL NAME:	HVPS Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2003
-------------------------------------------------------------------------
*/

#include "hvps.h"


/* -------------------------------------------------------------------- */
HVPS::HVPS(NcFile *file, NcVar *av) : Probe(file, av)
{
  tasIdx = concIdx = dbarIdx = lwIdx = dispIdx = dbzIdx = -1;

  for (int i = 0; i < nOtherVars(); ++i)
    {
    if (strcmp(otherVars[i]->name(), "TASX") == 0)
      tasIdx = i;

    if (strncmp(otherVars[i]->name(), "CONC", 5) == 0)
      concIdx = i;

    if (strncmp(otherVars[i]->name(), "PLWC", 4) == 0)
      lwIdx = i;

    if (strncmp(otherVars[i]->name(), "DBAR", 4) == 0)
      dbarIdx = i;

    if (strncmp(otherVars[i]->name(), "DISP", 4) == 0)
      dispIdx = i;

    if (strncmp(otherVars[i]->name(), "DBZ", 3) == 0)
      dbzIdx = i;
    }

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void HVPS::ComputeConcentration(float *accum, float *conc, long countV[],
	float *otherVarData[])
{
  int	i, bin;
  float	*dia, *counts, *concentration, *tas;
  double vol;

  tas = otherVarData[tasIdx];

  for (i = 0; i < countV[0] * countV[1]; ++i)
    {
    counts = &accum[i * VectorLength()];
    concentration = &conc[i * VectorLength()];

    vol = tas[i] / dataRate * 200 * 203 * (256-80) * 1.0e-5;

    for (bin = FirstBin(); bin <= LastBin(); ++bin)
      sampleVolume[bin] = vol;

    dia = midPointDiam;

#define PLWC
#define DBZ

#include "pms1d_cv"

    otherVarData[concIdx][i] = totalConcen;
    otherVarData[lwIdx][i] = plwc;
    otherVarData[dbarIdx][i] = dbar;
    otherVarData[dispIdx][i] = disp;
    otherVarData[dbzIdx][i] = dbz;
    }

}	/* END COMPUTECONCENTRATION */

/* END HVPS.CC */
