/*
-------------------------------------------------------------------------
OBJECT NAME:	2D_P.h

FULL NAME:	2D_P

TYPE:		Derived class

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2000
-------------------------------------------------------------------------
*/

#ifndef TWODP_H
#define TWODP_H

#include "define.h"
#include "netcdf.hh"

#include "Probe200.h"


/* -------------------------------------------------------------------- */
class TwoDP : public Probe200 {

public:
	TwoDP(NcFile *file, NcVar *av);

  void	ComputeConcentration(float *accum, float *conc, long countV[],
		float *otherVarData[]);


private:

};	/* END 2D_P.H */

#endif
