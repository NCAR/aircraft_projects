/*
-------------------------------------------------------------------------
OBJECT NAME:    Canvas.cc
 
FULL NAME:      Generic X canvas manipulations
 
ENTRY POINTS:
 
DESCRIPTION:
 
REFERENCES:
 
REFERENCED BY:
 
NOTES:
 
COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "Canvas.h"


/* -------------------------------------------------------------------- */
Canvas::Canvas(Widget drawA) : w(drawA), dpy(XtDisplay(drawA)), win(XtWindow(drawA)), defaultGC(XDefaultGC(dpy, 0))
{
  Cardinal	n;
  Arg		args[2];

  pixMap = 0;

  n = 0;
  XtSetArg(args[n], XtNforeground, &foreground); ++n;
  XtSetArg(args[n], XtNbackground, &background); ++n;
  XtGetValues(drawA, args, n);

  Resize();
  Clear();

}       /* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void Canvas::Clear() const
{
  XSetForeground(dpy, defaultGC, background);
  XFillRectangle(dpy, pixMap, defaultGC, 0, 0, width, height);
  XSetForeground(dpy, defaultGC, foreground);

}	/* END CLEAR */

/* -------------------------------------------------------------------- */
void Canvas::ClearArea(int x, int y, int w, int h) const
{
  XSetForeground(dpy, defaultGC, background);
  XFillRectangle(dpy, pixMap, defaultGC, x, y, w, h);
  XSetForeground(dpy, defaultGC, foreground);

}	/* END CLEARAREA */

/* -------------------------------------------------------------------- */
void Canvas::ExposeAll() const
{
  XCopyArea(dpy, pixMap, win, defaultGC, 0, 0, width, height, 0, 0);

}       /* END EXPOSEALL */
 
/* -------------------------------------------------------------------- */
void Canvas::ExposeArea(XmDrawingAreaCallbackStruct *call) const
{
  XExposeEvent *evt = (XExposeEvent *)call->event;

  XCopyArea(dpy, pixMap, win, defaultGC,
            evt->x, evt->y, evt->width, evt->height, evt->x, evt->y);

}       /* END EXPOSEAREA */
 
/* -------------------------------------------------------------------- */
void Canvas::Resize()
{
  Cardinal	n;
  Arg		args[5];

  n = 0;
  XtSetArg(args[n], XmNwidth, &width); ++n;
  XtSetArg(args[n], XmNheight, &height); ++n;
  XtSetArg(args[n], XtNdepth, &depth); ++n;
  XtGetValues(w, args, n);

  if (pixMap)
    XFreePixmap(dpy, pixMap);

  pixMap = XCreatePixmap(dpy, win, width, height, depth);

}       /* END RESIZE */

/* -------------------------------------------------------------------- */
void Canvas::SetSize(int ht, int wd)
{
  Cardinal	n;
  Arg		args[2];

  height = ht;
  width = wd;

  n = 0;
  XtSetArg(args[n], XmNwidth, width); ++n;
  XtSetArg(args[n], XmNheight, height); ++n;
  XtSetValues(w, args, n);

}	/* END SETSIZE */

/* END CANVAS.CC */
