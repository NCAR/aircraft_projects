/*
-------------------------------------------------------------------------
OBJECT NAME:	VarsWin.h

FULL NAME:	View Housekeeping & derived variables

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1998
-------------------------------------------------------------------------
*/

#ifndef VARSWIN_H
#define VARSWIN_H

#include "define.h"

#include "SetMgr.h"
#include "PlotMgr.h"
#include "TextWindow.h"


/* -------------------------------------------------------------------- */
class VarsWin : public TextWindow {

public:

	VarsWin(const Widget parent);

  void	Update(SetManager& sets, PlotManager *plotMgr);

private:

};	/* END VARSWIN.H */

#endif
