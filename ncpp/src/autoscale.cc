/*
-------------------------------------------------------------------------
OBJECT NAME:	autoscale.c

FULL NAME:	Friend functions to move min/max from SetMgr to Panel

ENTRY POINTS:	AutoScaleAccum()
		AutoScaleConc()
		AutoScaleSurface()
		AutoScaleVolume()

STATIC FNS:	none

DESCRIPTION:	

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "define.h"

#include "SetMgr.h"
#include "Panel.h"

//using namespace std;

/* -------------------------------------------------------------------- */
void AutoScaleAccum(SetManager& sets, Panel *panel)
{
  if (panel->AutoScale)
    {
    panel->xAxis.min = panel->xAxis.logScale ? 1.0 : sets.minBin;
    panel->xAxis.max = panel->xAxis.logScale ? 100.0 : sets.maxBin;
 
    panel->yAxis.min = panel->yAxis.logScale ? 1.0 : 0.0;

    if (sets.maxAccum > 0)
      panel->yAxis.max = pow10(ceil(log10((double)sets.maxAccum)));

    if (panel->yAxis.min == panel->yAxis.max)
      panel->yAxis.max += 1.0;
    }

}	/* END AUTOSCALE */

/* -------------------------------------------------------------------- */
void AutoScaleConc(SetManager& sets, Panel *panel)
{
  if (!panel->AutoScale)
    return;

  if (panel->xAxis.logScale)
    {
    panel->xAxis.min = pow10(floor(log10(sets.minCell)));
    panel->xAxis.max = pow10(ceil(log10(sets.maxCell)));
    }
  else
    {
    panel->xAxis.min = 0.0;
    panel->xAxis.max = sets.maxCell;
    }

  if (panel->yAxis.logScale)
    {
    if (sets.minConc <= 0.0)
      panel->yAxis.min = 0.01;
    else
      panel->yAxis.min = pow10(floor(log10(sets.minConc)));
    panel->yAxis.max = pow10(ceil(log10(sets.maxConc)));
    }
  else
    {
    panel->yAxis.min = 0.0;
    panel->yAxis.max = sets.maxConc;
    }

  if (sets.maxConc == 0.0)
    panel->yAxis.max = 10.0;

  if (panel->yAxis.min == panel->yAxis.max)
    panel->yAxis.max += 10.0;

}	/* END AUTOSCALE */

/* -------------------------------------------------------------------- */
void AutoScaleSurface(SetManager& sets, Panel *panel)
{
  if (!panel->AutoScale)
    return;

  if (panel->xAxis.logScale)
    {
    panel->xAxis.min = pow10(floor(log10(sets.minCell)));
    panel->xAxis.max = pow10(ceil(log10(sets.maxCell)));
    }
  else
    {
    panel->xAxis.min = 0.0;
    panel->xAxis.max = sets.maxCell;
    }

  if (panel->yAxis.logScale)
    {
    if (sets.minConc <= 0.0)
      panel->yAxis.min = 0.01;
    else
      panel->yAxis.min = pow10(floor(log10(sets.minSurf)));
    panel->yAxis.max = pow10(ceil(log10(sets.maxSurf)));
    }
  else
    {
    panel->yAxis.min = 0.0;
    panel->yAxis.max = sets.maxSurf;
    }

  if (sets.maxSurf == 0.0)
    panel->yAxis.max = 10.0;

  if (panel->yAxis.min == panel->yAxis.max)
    panel->yAxis.max += 10.0;

}	/* END AUTOSCALE */

/* -------------------------------------------------------------------- */
void AutoScaleVolume(SetManager& sets, Panel *panel)
{
  if (!panel->AutoScale)
    return;

  if (panel->xAxis.logScale)
    {
    panel->xAxis.min = pow10(floor(log10(sets.minCell)));
    panel->xAxis.max = pow10(ceil(log10(sets.maxCell)));
    }
  else
    {
    if (sets.minConc <= 0.0)
      panel->yAxis.min = 0.01;
    else
      panel->yAxis.min = pow10(floor(log10(sets.minVol)));
    panel->xAxis.max = sets.maxCell;
    }

  if (panel->yAxis.logScale)
    {
    panel->yAxis.min = 0.01;
    panel->yAxis.max = pow10(ceil(log10(sets.maxVol)));
    }
  else
    {
    panel->yAxis.min = 0.0;
    panel->yAxis.max = sets.maxVol;
    }

  if (sets.maxVol == 0.0)
    panel->yAxis.max = 10.0;

  if (panel->yAxis.min == panel->yAxis.max)
    panel->yAxis.max += 10.0;

}	/* END AUTOSCALE */

/* AUTOSCALE.CC */
