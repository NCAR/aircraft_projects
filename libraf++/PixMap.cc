/*
-------------------------------------------------------------------------
OBJECT NAME:    PixMap.cc
 
FULL NAME:      Generic X Pixmap manipulations
 
ENTRY POINTS:
 
DESCRIPTION:
 
REFERENCES:
 
REFERENCED BY:
 
NOTES:
 
COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "PixMap.h"


/* -------------------------------------------------------------------- */
PixMap::PixMap(const Widget w, int wd, int ht)
{
  Cardinal	n;
  Arg		args[4];
  int		depth;

  dpy = XtDisplay(w);
  win = XtWindow(w);
  defaultGC = XDefaultGC(dpy, 0);

  height = ht;
  width = wd;

  n = 0;
  XtSetArg(args[n], XtNforeground, &foreground); ++n;
  XtSetArg(args[n], XtNbackground, &background); ++n;
  XtSetArg(args[n], XtNdepth, &depth); ++n;
  XtGetValues(w, args, n);

  pixMap = XCreatePixmap(dpy, win, width, height, depth);

  Clear();

}       /* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
PixMap::~PixMap()
{
  if (pixMap)
    XFreePixmap(dpy, pixMap);

}	/* END DESTRUCTOR */

/* -------------------------------------------------------------------- */
void PixMap::Clear() const
{
  XSetForeground(dpy, defaultGC, background);
  XFillRectangle(dpy, pixMap, defaultGC, 0, 0, width, height);
  XSetForeground(dpy, defaultGC, foreground);

}	/* END CLEAR */

/* -------------------------------------------------------------------- */
void PixMap::Copy() const
{

}       /* END RESIZE */

/* END PIXMAP.CC */
