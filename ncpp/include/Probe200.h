/*
-------------------------------------------------------------------------
OBJECT NAME:	Probe200.h

FULL NAME:	260x, 200x, 200y

TYPE:		Base class

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1999
-------------------------------------------------------------------------
*/

#ifndef PROBE200_H
#define PROBE200_H

#include "define.h"
#include "netcdf.hh"

#include "Probe.h"


/* -------------------------------------------------------------------- */
class Probe200 : public Probe {

public:
	Probe200(NcFile *file, NcVar *av);

  friend class EditDiameters;

  virtual void	ComputeConcentration(float *accum, float *conc, long countV[],
		float *otherVarData[]);

  void	UpdateCellDiams(const int first, const int last, const float *newDiams);

  virtual int   SetEditWindow(Widget txt[]);
  virtual int   ApplyEditWindow(Widget txt[]);


protected:
  void		ComputeWidths(), ComputeDOF(float tasx);

  static const float	diodeDiameter = 0.2;

  int	nDiodes;
  float	responseTime, armDistance, PLWfac, DENS, DBZfac;
  float	sampleVolume[64], radius[64], esw[64], dof[64], mag,
		totalConcen, dbar, plwc, disp, dbz;

  int	tasIdx;						// Inputs
  int	concIdx, lwIdx, dbarIdx, dispIdx, dbzIdx;	// Outputs

};	/* END PROBE200.H */

#endif
