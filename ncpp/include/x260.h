/*
-------------------------------------------------------------------------
OBJECT NAME:	x260.h

FULL NAME:	260X

TYPE:		Derived class

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1999
-------------------------------------------------------------------------
*/

#ifndef X260_H
#define X260_H

#include "define.h"
#include "netcdf.hh"

#include "Probe200.h"


/* -------------------------------------------------------------------- */
class X260 : public Probe200 {

public:
	X260(NcFile *file, NcVar *av);

  void	ComputeConcentration(float *accum, float *conc, long countV[],
		float *otherVarData[]);


private:

};	/* END X260.H */

#endif
