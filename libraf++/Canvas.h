/*
-------------------------------------------------------------------------
OBJECT NAME:	Canvas.h

FULL NAME:	Generic X canvas

TYPE:		Abstract

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef CANVAS_H
#define CANVAS_H

#include <Xm/Xm.h>

/* -------------------------------------------------------------------- */
class Canvas {

public:
		Canvas(Widget w);

  void		Clear() const;
  void		ClearArea(int x, int y, int w, int h) const;
  void		ExposeArea(XmDrawingAreaCallbackStruct *call) const;
  void		ExposeAll() const;
  void          Resize();
  void          SetSize(const int height, const int width);

  int		Height() const	{ return(height); }
  int		Width()	 const	{ return(width); }
  int		Depth()	 const	{ return(depth); }

  const Widget	Wdgt() const	{ return(w); }
  Drawable	Surface() const	{ return(pixMap); }

  int		PutImage(XImage *im, int x, int y, int w, int h)
	        { return(XPutImage(dpy, pixMap, defaultGC, im, 0, 0, x, y, w, h)); }

  XImage	*GetImage(int x, int y, int w, int h)
	        { return(XGetImage(dpy, pixMap, x, y, w, h,
			(unsigned long)AllPlanes, ZPixmap)); }


private:
  Widget	w;
  Display	*dpy;
  Window	win;
  Pixmap	pixMap;
  GC		defaultGC;

  short		width, height;
  int		depth;

  unsigned long	foreground, background;

};	/* END CANVAS.H */

#endif
/* Silly comments for testing
One
two
three
four
five
a line to delete
another line to delete
another line to delete
a line to change
another line to delete
another line to delete
*/
