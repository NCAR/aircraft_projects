/*
-------------------------------------------------------------------------
OBJECT NAME:	s100.h

FULL NAME:	DMT modified FSSP-100

TYPE:		Derived class

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2000
-------------------------------------------------------------------------
*/

#ifndef S100_H
#define S100_H

#include "define.h"
#include "netcdf.hh"

#include "Probe.h"


/* -------------------------------------------------------------------- */
class S100 : public Probe {

public:
	S100(NcFile *file, NcVar *av);

  friend class EditDiameters;

  void	ComputeConcentration(float *accum, float *conc, long countV[],
		float *otherVarData[]);
  float CellSize(int idx)       { return(diameter[idx + (range << 4)]); }
  float BinWidth(int idx)       { return(binWidth[idx + (range << 4)]); }

  void	SetRange(int newRange)	{ range = (newRange < 0 ? 0 : newRange); }

private:
  int	range, rangeIdx;

  float	PLWfac, DBZfac, DENS, DOF, beamDiameter;
  float	sampleVolume[41], totalConcen, dbar, plwc, disp, dbz;

  int	tasIdx, rejATIdx, oFlowIdx;			// Inputs
  int	concIdx, lwIdx, dbzIdx, dbarIdx, dispIdx;	// Outputs

};	/* END S100.H */

#endif
