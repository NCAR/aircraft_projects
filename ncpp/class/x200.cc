/*
-------------------------------------------------------------------------
OBJECT NAME:	x200.cc

FULL NAME:	200X Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1999
-------------------------------------------------------------------------
*/

#include "x200.h"


/* -------------------------------------------------------------------- */
X200::X200(NcFile *file, NcVar *av) : Probe200(file, av)
{
  NcAtt		*attr;

  if ((attr = avar->get_att("nDiodes")))
    nDiodes = attr->as_int(0);
  else
    nDiodes = 15;

  if ((attr = avar->get_att("ArmDistance")))
    armDistance = attr->as_float(0);
  else
    armDistance = 61.0;

  ComputeWidths();

}	/* END CONSTRUCTOR */

/* END X200.CC */
