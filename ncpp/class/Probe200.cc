/*
-------------------------------------------------------------------------
OBJECT NAME:	Probe200.cc

FULL NAME:	260X, 200X, 200Y Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1999
-------------------------------------------------------------------------
*/

#include "Probe200.h"


/* -------------------------------------------------------------------- */
Probe200::Probe200(NcFile *file, NcVar *av) : Probe(file, av)
{
  NcAtt		*attr;

  if ((attr = avar->get_att("ResponseTime")))
    responseTime = attr->as_float(0);
  else
    responseTime = 0.35;

  if ((attr = avar->get_att("PLWfactor")))
    PLWfac = attr->as_float(0);
  else
    PLWfac = 1.0e-9;

  if ((attr = avar->get_att("Density")))
    DENS = attr->as_float(0);
  else
    DENS = 1.0;

  ComputeWidths();

  for (int i = 0; i < nOtherVars(); ++i)
    {
    if (strcmp(otherVars[i]->name(), "TASX") == 0)
      tasIdx = i;


    if (strncmp(otherVars[i]->name(), "CONC", 4) == 0)
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
void Probe200::ComputeConcentration(float *accum, float *conc, long countV[],
	float *otherVarData[])
{
  int	time, bin;
  float	*dia, *counts, *concentration;
  float	*tas, tasx;

  tas = otherVarData[tasIdx];

  for (time = 0; time < countV[0] * countV[1]; ++time)
    {
    counts = &accum[time * VectorLength()];
    concentration = &conc[time * VectorLength()];

    tasx = tas[time] / dataRate;

    ComputeDOF(tasx);

    for (bin = FirstBin(); bin <= LastBin(); ++bin)
      sampleVolume[bin] = tasx * (dof[bin] * esw[bin]);

    dia = midPointDiam;

#define PLWC

#include "pms1d_cv"

    otherVarData[concIdx][time] = totalConcen;
    otherVarData[lwIdx][time] = plwc;
    otherVarData[dbarIdx][time] = dbar;
    otherVarData[dispIdx][time] = disp;
    }

}	/* END COMPUTECONCENTRATION */

/* -------------------------------------------------------------------- */
void Probe200::UpdateCellDiams(const int first, const int last, const float *newDiams)
{
  Probe::UpdateCellDiams(first, last, newDiams);
  ComputeWidths();

}       /* END UPDATECELLDIAMS */

/* -------------------------------------------------------------------- */
void Probe200::ComputeWidths()
{
  Probe::ComputeWidths();

  // All binWidths should be equal for 200 series probes.
  mag = diodeDiameter / (binWidth[1] / 1000);

  for (int i = 1; i <= LastBin(); ++i)
    {
    radius[i]   = midPointDiam[i] / 2000;
    esw[i]      = diodeDiameter * (nDiodes - i - 1) / mag;
    }

}	/* END COMPUTEWIDTHS */

/* -------------------------------------------------------------------- */
void Probe200::ComputeDOF(float tasx)
{
  int		i;
  double	szz, timex, frac, f, z;
responseTime = 0.001;
  for (i = FirstBin(); i <= LastBin(); ++i)
    {
    /* Determine size in terms of # of array elements
     */
    szz = 2.0 * radius[i];

    /* Diminish this radius by an amount that accounts for
     * the fact that the particle is not on the diode array
     * 100% of the time 50% shadowed. This amount is approximately
     * one half diode array width wide.
     */
    szz += (diodeDiameter / mag) / 2.0;

    /* Calculate amount of time particle will be on the array
     */
    timex = szz / (tasx * 1000.0) * 1.0e6;

    /* This is the fraction of total amplitude caused by response
     * time
     */
    frac = (double)1.0 - exp((double)-timex / responseTime);

    /* Have to meet 70% occultation for the 1D.
     */
    if (frac < 0.7)
      dof[i] = 0.0;
    else
      /* Cautionary note to users of this routine, the relationship
       * between dof and Z was derived from laboratory studies which
       * are somewhat prelimnary in nature and need additional
       * verification, A new algorithm should be available by 9/1/92
       */
      {
      f = (0.7 / frac) * 100.0;
      z = 30.46 - 0.628 * f + 0.003246 * f * f;
      dof[i] = 1580.0 * z * radius[i] * radius[i];
      }

    if (dof[i] > armDistance)
      dof[i] = armDistance;
    }

}	/* END COMPUTEDOF */

/* -------------------------------------------------------------------- */
int Probe200::SetEditWindow(Widget text[])
{
  return(Probe::SetEditWindow(text));

}

/* -------------------------------------------------------------------- */
int Probe200::ApplyEditWindow(Widget text[])
{
  return(Probe::ApplyEditWindow(text));

}

/* END PROBE200.CC */
