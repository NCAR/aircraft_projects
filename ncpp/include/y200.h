/*
-------------------------------------------------------------------------
OBJECT NAME:	y200.h

FULL NAME:	200Y

TYPE:		Derived class

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1999
-------------------------------------------------------------------------
*/

#ifndef Y200_H
#define Y200_H

#include "define.h"
#include "netcdf.hh"

#include "Probe200.h"


/* -------------------------------------------------------------------- */
class Y200 : public Probe200 {

public:
	Y200(NcFile *file, NcVar *av);


private:

};	/* END Y200.H */

#endif
