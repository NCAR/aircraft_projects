/*
-------------------------------------------------------------------------
OBJECT NAME:	s200.h

FULL NAME:	DMT ASAS/PCASP

TYPE:		Derived class

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2001
-------------------------------------------------------------------------
*/

#ifndef S200_H
#define S200_H

#include "define.h"
#include "netcdf.hh"

#include "Probe.h"


/* -------------------------------------------------------------------- */
class S200 : public Probe {

public:
	S200(NcFile *file, NcVar *av);

  void	ComputeConcentration(float *accum, float *conc, long countV[],
		float *otherVarData[]);


private:
  float	sampleVolume[41], totalConcen, dbar, pvol, disp;

  int	actIdx, flowIdx;			// Inputs
  int	concIdx, dbarIdx, dispIdx, volIdx;	// Outputs

};	/* END S200.H */

#endif
