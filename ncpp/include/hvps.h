/*
-------------------------------------------------------------------------
OBJECT NAME:	hvps.h

FULL NAME:	HVPS

TYPE:		Derived class

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2003
-------------------------------------------------------------------------
*/

#ifndef HVPS_H
#define HVPS_H

#include "define.h"
#include "netcdf.hh"

#include "Probe.h"


/* -------------------------------------------------------------------- */
class HVPS : public Probe {

public:
	HVPS(NcFile *file, NcVar *av);

  void	ComputeConcentration(float *accum, float *conc, long countV[],
		float *otherVarData[]);

private:
  float	PLWfac, DBZfac, DENS;
  float	sampleVolume[256], totalConcen, dbar, plwc, dbz, disp;

  int	tasIdx;				// Inputs
  int	concIdx, dbarIdx, lwIdx, dispIdx, dbzIdx;	// Outputs

};	/* END HVPS.H */

#endif
