/*
-------------------------------------------------------------------------
OBJECT NAME:    XPen.cc
 
FULL NAME:      Plot canvas
 
ENTRY POINTS:
 
DESCRIPTION:
 
REFERENCES:
 
REFERENCED BY:
 
NOTES:
 
COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "XPen.h"


/* -------------------------------------------------------------------- */
XPen::XPen(Widget w)
{
  Arg           args[4];
  Cardinal      n;
  unsigned long	valuemask;
  XGCValues	values;

  dpy = XtDisplay(w);

  n = 0;
  XtSetArg(args[n], XtNforeground, &values.foreground); ++n;
  XtSetArg(args[n], XtNbackground, &values.background); ++n;
  XtGetValues(w, args, n);

  valuemask = GCForeground | GCBackground;
 
  gc = XCreateGC(dpy, RootWindowOfScreen(XtScreen(w)), valuemask, &values);
  lineWidth = 1;
 
}       /* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void XPen::SetClipping(int x, int y, int h, int w)
{
  XRectangle  clip_area[1];
 
  /* Set clipping so that graph data cannot exceed box boundries
   */
  clip_area[0].x = x;
  clip_area[0].y = y;
  clip_area[0].width = h;
  clip_area[0].height = w;
  XSetClipRectangles(dpy, gc, 0, 0, clip_area, 1, Unsorted);

}	/* END SETCLIPPING */

/* -------------------------------------------------------------------- */
void XPen::SetDash(int n)
{
  char	dashList[4];

  XSetLineAttributes(dpy, gc, lineWidth, LineOnOffDash, CapButt, JoinMiter);

  dashList[0] = (n + 1) * 6;
  dashList[1] = (n + 1) * 3;
  XSetDashes(dpy, gc, 0, dashList, 2);

}	/* END SETDASH */

/* -------------------------------------------------------------------- */
XImage *XPen::GetImage(Drawable canvas, int x, int y, int width, int height)
{
  return(XGetImage(dpy, canvas, x, y, width, height, 0xffffffff, XYPixmap));

}

/* -------------------------------------------------------------------- */
unsigned long XPen::GetBackground()
{
  XGCValues	v;

  XGetGCValues(dpy, gc, GCBackground, &v);

  return(v.background);

}	/* END GETBACKGROUND */

/* END XPEN.CC */
