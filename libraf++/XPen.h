/*
-------------------------------------------------------------------------
OBJECT NAME:	XPen.h

FULL NAME:	Generic X Graphics Context and Font class

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef XPEN_H
#define XPEN_H

#include <X11/Intrinsic.h>
#include <X11/StringDefs.h>

#include <string>
#include <cstdio>

/* -------------------------------------------------------------------- */
class XPen {

public:
	XPen(Widget w);

  void	SetFont(const XFontStruct *font) { XSetFont(dpy, gc, font->fid); }
  void	SetColor(unsigned long color)	{ XSetForeground(dpy, gc, color); }
  void	SetLineWidth(int w)	{ if (w > 0 && w < 10)
    XSetLineAttributes(dpy, gc, (lineWidth=w), LineSolid, CapButt, JoinMiter); }

  void	SetLineStyle(int n);	// For drawing data sets.

  void	SetFunction(int mask)	{ XSetFunction(dpy, gc, mask); }

  
  void	DrawText(Drawable canvas, int x, int y, char str[])
	{ XDrawString(dpy, canvas, gc, x, y, str, strlen(str)); }

  void	DrawText(Drawable canvas, int x, int y, const std::string& str)
	{ XDrawString(dpy, canvas, gc, x, y, str.c_str(), str.length()); }

  void	DrawPoint(Drawable canvas, int x, int y)
	{ XDrawPoint(dpy, canvas, gc, x, y); }

  void	DrawPoints(Drawable canvas, XPoint pts[], int nPts)
	{ XDrawPoints(dpy, canvas, gc, pts, nPts, CoordModeOrigin); }

  void	DrawLine(Drawable canvas, int x, int y, int x1, int y1)
	{ XDrawLine(dpy, canvas, gc, x, y, x1, y1); }

  void	DrawLines(Drawable canvas, XPoint pts[], int nPts)
	{ XDrawLines(dpy, canvas, gc, pts, nPts, CoordModeOrigin); }

  void	DrawRectangle(Drawable canvas, int x, int y, int w, int h)
	{ XDrawRectangle(dpy, canvas, gc, x, y, w, h); }

  void	DrawRectangles(Drawable canvas, XRectangle rex[], int nRex)
	{ XDrawRectangles(dpy, canvas, gc, rex, nRex); }

  void	DrawRectangleFilled(Drawable canvas, int x, int y, int w, int h)
	{ XFillRectangle(dpy, canvas, gc, x, y, w, h); }

  void	SetClipping(int x, int y, int w, int h);
  void	ClearClipping()		{ XSetClipMask(dpy, gc, None); }

  void  SetDash(int n);
  void	ClearDash()
	{ XSetLineAttributes(dpy, gc, lineWidth, LineSolid, CapButt, JoinMiter); }


  XImage *GetImage(Drawable canvas, int x, int y, int width, int height);

  void	PutImage(Drawable dest, XImage *src, int src_x, int src_y, int dst_x,
	int dst_y, int w, int h)
	{ XPutImage(dpy, dest, gc, src, src_x, src_y, dst_x, dst_y, w, h); }


  unsigned long	GetBackground();


private:
  Display	*dpy;
  GC		gc;

  int		lineWidth;

};	/* END XPEN.H */

#endif
