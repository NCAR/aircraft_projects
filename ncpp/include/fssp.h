/*
-------------------------------------------------------------------------
OBJECT NAME:	fssp.h

FULL NAME:	FSSP-100

TYPE:		Derived class

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1999
-------------------------------------------------------------------------
*/

#ifndef FSSP_H
#define FSSP_H

#include "define.h"
#include "netcdf.hh"

#include "Probe.h"


/* -------------------------------------------------------------------- */
class FSSP : public Probe {

public:
	FSSP(NcFile *file, NcVar *av);

  friend class EditDiameters;

  void	ComputeConcentration(float *accum, float *conc, long countV[],
		float *otherVarData[]);
  float CellSize(int idx)       { return(diameter[idx + (range << 4)]); }
  float BinWidth(int idx)       { return(binWidth[idx + (range << 4)]); }

  void	SetRange(int newRange)	{ range = (newRange < 0 ? 0 : newRange); }

private:
  int	range, rangeIdx;

  float	PLWfac, DBZfac, DENS, DOF, beamDiameter;
  float	sampleVolume[16], totalConcen, dbar, plwc, disp, dbz;

  int	tasIdx, actIdx, bmFrIdx;			// Inputs
  int	concIdx, lwIdx, dbzIdx, dbarIdx, dispIdx;	// Outputs

};	/* END FSSP.H */

#endif
