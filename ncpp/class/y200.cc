/*
-------------------------------------------------------------------------
OBJECT NAME:	y200.cc

FULL NAME:	200Y Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1999
-------------------------------------------------------------------------
*/

#include "y200.h"


/* -------------------------------------------------------------------- */
Y200::Y200(NcFile *file, NcVar *av) : Probe200(file, av)
{
  NcAtt		*attr;

  if ((attr = avar->get_att("nDiodes")))
    nDiodes = attr->as_int(0);
  else
    nDiodes = 24;

  if ((attr = avar->get_att("ArmDistance")))
    armDistance = attr->as_float(0);
  else
    armDistance = 263.0;

  ComputeWidths();

}	/* END CONSTRUCTOR */

/* END Y200.CC */
