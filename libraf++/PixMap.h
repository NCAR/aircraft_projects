/*
-------------------------------------------------------------------------
OBJECT NAME:	PixMap.h

FULL NAME:	Generic X Pixmap

TYPE:		Abstract

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef PIXMAP_H
#define PIXMAP_H

#include <X11/Intrinsic.h>
#include <X11/StringDefs.h>


/* -------------------------------------------------------------------- */
class PixMap {

public:
		PixMap(Widget w, int w, int h);
		~PixMap();

  void		Clear() const;
  void		Copy() const;

  Drawable	Surface() const	{ return(pixMap); }

  XImage
	*GetImage(int w, int h)
	{ return(XGetImage(dpy, pixMap, 0, 0, w, h, 0xFFFFFFFF, XYPixmap)); }

  int	PutImage(XImage *im, int x, int y, int w, int h)
	{ return(XPutImage(dpy, pixMap, defaultGC, im, 0, 0, x, y, w, h)); }


private:
  Display	*dpy;
  Window	win;
  GC		defaultGC;
  Pixmap	pixMap;

  short		width, height;
  int		depth;

  unsigned long	foreground, background;

};	/* END PIXMAP.H */

#endif
