/*
-------------------------------------------------------------------------
OBJECT NAME:	Probe.cc

FULL NAME:	Probe Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "Probe.h"


/* -------------------------------------------------------------------- */
Probe::Probe(char name[], int recSize)
{
  strncpy(Name, name, 2); Name[2] = '\0';
  strcpy(Code, Name);
  strcpy(SerialNum, "");

  lrLen = recSize;
  lrPpr = 1;
  displayed = false;

  if (Name[0] == 'C')
    Resolution = 25;

  if (Name[0] == 'P')
    Resolution = 200;

printf("Probe:: %s, resolution = %d\n", Name, Resolution);

}

/* -------------------------------------------------------------------- */
Probe::Probe(Header *hdr, Pms2 *p, int cnt)
{

  // Extract stuff from Header.
  strcpy(Name, hdr->VariableName(p));
  strcat(Name, "_");
  strcat(Name, hdr->AircraftLocation(p));
  strcpy(SerialNum, hdr->SerialNumber(p));

  Code[0] = Name[3]; Code[1] = cnt + '0'; Code[2] = '\0';

  lrLen = hdr->lrLength(p);
  lrPpr = hdr->lrPpr(p);
  Resolution = hdr->Resolution(p);
  displayed = false;

printf("Probe:: %s - %s\n", Name, Code);

}	/* END CONSTRUCTOR */

/* END PROBE.CC */
