/*
-------------------------------------------------------------------------
OBJECT NAME:	Cursor.h

FULL NAME:	Cursor's

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef CURSOR_H
#define CURSOR_H

#include <X11/Intrinsic.h>
#include <X11/StringDefs.h>
#include <X11/cursorfont.h>


/* -------------------------------------------------------------------- */
class XCursor {

public:
  enum mode { POINTER, WAIT, ANNOTATE, GRAB };

	XCursor();

  void	WaitCursor(Widget w);
  void	PointerCursor(Widget w);
  void	TextCursor(Widget w);
  void	GrabCursor(Widget w);

  mode	cursorMode;

private:

  Cursor waitCursor;
  Cursor textCursor;
  Cursor grabCursor;
  Cursor pointerCursor;


};	/* END CURSOR.H */

#endif
