/*
-------------------------------------------------------------------------
OBJECT NAME:	f300.h

FULL NAME:	FSSP-300

TYPE:		Derived class

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1999
-------------------------------------------------------------------------
*/

#ifndef F300_H
#define F300_H

#include "define.h"
#include "netcdf.hh"

#include "Probe.h"


/* -------------------------------------------------------------------- */
class F300 : public Probe {

public:
	F300(NcFile *file, NcVar *av);

  void	ComputeConcentration(float *accum, float *conc, long countV[],
		float *otherVarData[]);

private:
  float	sampleVolume[41], totalConcen, dbar, pvol, disp;

  int	tasIdx;				// Inputs
  int	concIdx, dbarIdx, volIdx;	// Outputs

};	/* END F300.H */

#endif
