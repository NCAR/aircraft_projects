/*
-------------------------------------------------------------------------
OBJECT NAME:	2D_C.h

FULL NAME:	2D_C

TYPE:		Derived class

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2000
-------------------------------------------------------------------------
*/

#ifndef TWODC_H
#define TWODC_H

#include "define.h"
#include "netcdf.hh"

#include "Probe200.h"


/* -------------------------------------------------------------------- */
class TwoDC : public Probe200 {

public:
	TwoDC(NcFile *file, NcVar *av);

  void	ComputeConcentration(float *accum, float *conc, long countV[],
		float *otherVarData[]);


private:

};	/* END 2D_C.H */

#endif
