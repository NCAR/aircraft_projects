/*
-------------------------------------------------------------------------
OBJECT NAME:	XmError.h

FULL NAME:	Motif Error dialog.

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef XMERROR_H
#define XMERROR_H

#include <Xm/Xm.h>
#include <Xm/MessageB.h>


/* -------------------------------------------------------------------- */
class XmError {

public:
  XmError(Widget parent, char str[]);

private:
  Widget	errorBox;

};	/* END XMERROR.H */

#endif
