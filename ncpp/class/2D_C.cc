/*
-------------------------------------------------------------------------
OBJECT NAME:	2D_C.cc

FULL NAME:	2D C Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2000
-------------------------------------------------------------------------
*/

#include "2D_C.h"


/* -------------------------------------------------------------------- */
TwoDC::TwoDC(NcFile *file, NcVar *av) : Probe200(file, av)
{
  NcAtt		*attr;

  if ((attr = avar->get_att("nDiodes")))
    nDiodes = attr->as_int(0);
  else
    nDiodes = 32;

  if ((attr = avar->get_att("ArmDistance")))
    armDistance = attr->as_float(0);
  else
    armDistance = 61.0;

  if ((attr = avar->get_att("DBZfactor")))
    DBZfac = attr->as_float(0);
  else
    DBZfac = 1.0e3;

  ComputeWidths();

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void TwoDC::ComputeConcentration(float *accum, float *conc, long countV[],
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

    // EAW is a hard 0.8 for all bins.
    for (bin = FirstBin(); bin <= LastBin(); ++bin)
      sampleVolume[bin] = tasx * (dof[bin] * 0.8) * 0.001;

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

/* END 2D_C.CC */
