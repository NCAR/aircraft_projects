/*
-------------------------------------------------------------------------
OBJECT NAME:	XmWarn.h

FULL NAME:	Motif Warn dialog.

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef XMWARN_H
#define XMWARN_H

#include <Xm/Xm.h>
#include <Xm/MessageB.h>

/* -------------------------------------------------------------------- */
class XmWarn {

public:
  XmWarn(Widget parent, char warning[], XtCallbackProc okCB, XtCallbackProc cancelCB);

private:
  Widget	warnBox;

};	/* END XMWARN.H */

#endif
