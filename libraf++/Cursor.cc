/*
-------------------------------------------------------------------------
OBJECT NAME:	cursor.c

FULL NAME:	Cursors

ENTRY POINTS:	WaitCursor()
		TextCursor()
		PointerCursor()

STATIC FNS:	none

DESCRIPTION:	Create and remove various cursors.  Stop watch, text
		insert, etc.

REFERENCES:	none

REFERENCED BY:	dataIO.c, annotate.c

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "Cursor.h"


/* -------------------------------------------------------------------- */
XCursor::XCursor()
{
  cursorMode = POINTER;

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void XCursor::WaitCursor(Widget w)
{
  Display	*dpy;
  static bool	firstTime = true;

  if (w == NULL)
    return;

  dpy = XtDisplay(w);

  if (firstTime)
    {
    waitCursor = XCreateFontCursor(dpy, XC_watch);
    firstTime = false;
    }

  XDefineCursor(dpy, XtWindow(w), waitCursor);
  XFlush(dpy);

}	/* END WAITCURSOR */

/* -------------------------------------------------------------------- */
void XCursor::TextCursor(Widget w)
{
  Display	*dpy;
  static bool	firstTime = true;

  if (w == NULL)
    return;

  dpy = XtDisplay(w);

  if (firstTime)
    {
    textCursor = XCreateFontCursor(dpy, XC_xterm);
    firstTime = false;
    }

  XDefineCursor(dpy, XtWindow(w), textCursor);
  XFlush(dpy);
  cursorMode = ANNOTATE;

}	/* END TEXTCURSOR */

/* -------------------------------------------------------------------- */
void XCursor::GrabCursor(Widget w)
{
  Display	*dpy;
  static bool	firstTime = true;

  if (w == NULL)
    return;

  dpy = XtDisplay(w);

  if (firstTime)
    {
    grabCursor = XCreateFontCursor(dpy, XC_xterm);
    firstTime = false;
    }

  XDefineCursor(dpy, XtWindow(w), grabCursor);
  XFlush(dpy);
  cursorMode = GRAB;

}	/* END GRABCURSOR */

/* -------------------------------------------------------------------- */
void XCursor::PointerCursor(Widget w)
{
  Display	*dpy;
  static bool	firstTime = true;

  if (w == NULL)
    return;

  dpy = XtDisplay(w);

  if (firstTime)
    {
    pointerCursor = XCreateFontCursor(dpy, XC_left_ptr);
    firstTime = false;
    }

  XDefineCursor(dpy, XtWindow(w), pointerCursor);
  XFlush(dpy);
  cursorMode = POINTER;

}	/* END POINTERCURSOR */

/* END CURSOR.C */
