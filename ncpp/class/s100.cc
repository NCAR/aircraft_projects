/*
-------------------------------------------------------------------------
OBJECT NAME:	s100.cc

FULL NAME:	DMT modified FSSP-100 Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2000
-------------------------------------------------------------------------
*/

#include "s100.h"


/* -------------------------------------------------------------------- */
S100::S100(NcFile *file, NcVar *av) : Probe(file, av)
{
  NcAtt		*attr;

  if ((attr = avar->get_att("BeamDiameter")))
    beamDiameter = attr->as_float(0);
  else
    beamDiameter = 0.19;

  if ((attr = avar->get_att("DepthOfField")))
    DOF = attr->as_float(0);
  else
    DOF = 3.05;

  if ((attr = avar->get_att("Density")))
    DENS = attr->as_float(0);
  else
    DENS = 1.0;

  if ((attr = avar->get_att("PLWfactor")))
    PLWfac = attr->as_float(0);
  else
    PLWfac = 1.0e-6;

  if ((attr = avar->get_att("DBZfactor")))
    DBZfac = attr->as_float(0);
  else
    DBZfac = 1.0e6;

  range = 0;	// For FSSP, all other probes must be 0.

  for (int i = 0; i < nOtherVars(); ++i)
    {
    if (strcmp(otherVars[i]->name(), "TASX") == 0)
      tasIdx = i;

    if (strncmp(otherVars[i]->name(), "REJAT", 5) == 0)
      rejATIdx = i;

    if (strncmp(otherVars[i]->name(), "OVFLW", 5) == 0)
      oFlowIdx = i;


    if (strncmp(otherVars[i]->name(), "CONC", 4) == 0)
      concIdx = i;

    if (strncmp(otherVars[i]->name(), "PLWC", 4) == 0)
      lwIdx = i;

    if (strncmp(otherVars[i]->name(), "DBZF", 4) == 0)
      dbzIdx = i;

    if (strncmp(otherVars[i]->name(), "DBAR", 4) == 0)
      dbarIdx = i;

    if (strncmp(otherVars[i]->name(), "DISP", 4) == 0)
      dispIdx = i;
    }

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void S100::ComputeConcentration(float *accum, float *conc, long countV[],
	float *otherVarData[])
{
  int	i, bin;
  float	*dia, *counts, *concentration, total_cnts;
  float	*tas, *oFlow, *rejAT, sampleArea;
  double vol;

  tas = otherVarData[tasIdx];
  rejAT = otherVarData[rejATIdx];
  oFlow = otherVarData[oFlowIdx];

  sampleArea = DOF * beamDiameter;

  for (i = 0; i < countV[0] * countV[1]; ++i)
    {
    counts = &accum[i * VectorLength()];
    concentration = &conc[i * VectorLength()];

    total_cnts = counts[0];

    vol = tas[i] / dataRate * sampleArea;

    if (total_cnts > 0)
      vol *= total_cnts / (total_cnts + rejAT[i]);

    for (bin = FirstBin(); bin <= LastBin(); ++bin)
      sampleVolume[bin] = (float)vol;

    dia = &midPointDiam[range << 4];

#define PLWC
#define DBZ

#include "pms1d_cv"

    if (total_cnts > 0)
      {
      float	ccc = (total_cnts + oFlow[i]) / total_cnts;

      for (bin = FirstBin(); bin <= LastBin(); ++bin)
        concentration[bin] *= ccc;

      totalConcen *= ccc;
      }

    otherVarData[concIdx][i] = totalConcen;
    otherVarData[lwIdx][i] = plwc;
    otherVarData[dbarIdx][i] = dbar;
    otherVarData[dispIdx][i] = disp;
    otherVarData[dbzIdx][i] = dbz;
    }

}	/* END COMPUTECONCENTRATION */

/* END S100.CC */
