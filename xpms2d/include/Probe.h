/*
-------------------------------------------------------------------------
OBJECT NAME:	Probe.h

FULL NAME:	Probe Information

ENTRY POINTS:	

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef PROBE_H
#define PROBE_H

#include "define.h"

#include "hdrAPI.h"

/* -------------------------------------------------------------------- */
class Probe {

public:
  Probe(Header *hdr, Pms2 *p, int cnt);
  Probe(char hdr[], int recSize);

  char	Name[NAMELEN];
  char	Code[4];
  char	SerialNum[NAMELEN];
  long	lrLen;
  int	lrPpr;
  int	Resolution;

  bool	Display()		{ return(displayed); }
  void	setDisplay(bool b)	{ displayed = b; }

private:
  bool	displayed;

};	/* END PROBE.H */

#endif
