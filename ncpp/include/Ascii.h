/*
-------------------------------------------------------------------------
OBJECT NAME:	Ascii.h

FULL NAME:	View ASCII cell data.

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1998
-------------------------------------------------------------------------
*/

#ifndef ASCII_H
#define ASCII_H

#include "define.h"

#include "SetMgr.h"
#include "PlotMgr.h"
#include "TextWindow.h"


/* -------------------------------------------------------------------- */
class Ascii : public TextWindow {

public:

	Ascii(const Widget parent);

  void	Update(SetManager& sets, PlotManager *plotMgr);

private:

};	/* END ASCII.H */

#endif
