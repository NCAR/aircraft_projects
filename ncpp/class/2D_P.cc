/*
-------------------------------------------------------------------------
OBJECT NAME:	2D_P.cc

FULL NAME:	2D P Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2000
-------------------------------------------------------------------------
*/

#include "2D_P.h"


/* -------------------------------------------------------------------- */
TwoDP::TwoDP(NcFile *file, NcVar *av) : Probe200(file, av)
{
  NcAtt		*attr;

  if ((attr = avar->get_att("nDiodes")))
    nDiodes = attr->as_int(0);
  else
    nDiodes = 32;

  if ((attr = avar->get_att("ArmDistance")))
    armDistance = attr->as_float(0);
  else
    armDistance = 261.0;

  if ((attr = avar->get_att("DBZfactor")))
    DBZfac = attr->as_float(0);
  else
    DBZfac = 1.0e3;

  ComputeWidths();

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void TwoDP::ComputeConcentration(float *accum, float *conc, long countV[],
	float *otherVarData[])
{
  int	time, bin;
  float	*dia, *counts, *concentration;
  float	*tas, *fbmfr, *activity, tasx;

  tas = otherVarData[tasIdx];

  for (time = 0; time < countV[0] * countV[1]; ++time)
    {
    counts = &accum[time * VectorLength()];
    concentration = &conc[time * VectorLength()];

    tasx = tas[time] / dataRate;

    ComputeDOF(tasx);

    // EAW is a hard 6.4 for all bins.  Al Cooper.
    for (bin = FirstBin(); bin <= LastBin(); ++bin)
      sampleVolume[bin] = tasx * (dof[bin] * 6.4) * 0.001;

    dia = midPointDiam;

#define PLWC
#define DBZ

#include "pms1d_cv"

    otherVarData[concIdx][time] = totalConcen;
    otherVarData[lwIdx][time] = plwc;
    otherVarData[dbarIdx][time] = dbar;
    otherVarData[dispIdx][time] = disp;
    otherVarData[dbzIdx][time] = dbz;
    }

}	/* END COMPUTECONCENTRATION */

/* END 2D_P.CC */
