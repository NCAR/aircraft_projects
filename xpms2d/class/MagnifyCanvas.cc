/*
-------------------------------------------------------------------------
OBJECT NAME:    MagnifyCanvas.cc
 
FULL NAME:      Magnify canvas
 
ENTRY POINTS:
 
DESCRIPTION:
 
REFERENCES:
 
REFERENCED BY:
 
NOTES:
 
COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "MagnifyCanvas.h"
#include "Cursor.h"
#include "Magnify.h"
#include "MainCanvas.h"
#include "XPen.h"

extern XCursor		cursor;
extern Magnify		*mag;
extern MainCanvas	*mainPlot;
extern XPen		*pen;

#include <algorithm>


/* -------------------------------------------------------------------- */
MagnifyCanvas::MagnifyCanvas(Widget w) : Canvas(w)
{

}       /* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void MagnifyCanvas::draw()
{
  int		xIn, yIn, xOut, yOut, theWidth, theHeight;
  unsigned long	pix, background;
  XImage	*imageIn, *imageOut;

  if (mag->width <= 0 || mag->height <= 0)
    return;

  cursor.WaitCursor(mainPlot->Wdgt());
  cursor.WaitCursor(Wdgt());

  theWidth = std::min(mag->width, Width() >> 1);
  theHeight = std::min(mag->height, Height() >> 1);

  imageIn = pen->GetImage(mainPlot->Surface(),
                      mag->startX, mag->startY, theWidth, theHeight);

  Clear();
  imageOut = pen->GetImage(Surface(), 0, 0, theWidth << 1, theHeight << 1);

  background = pen->GetBackground();;

  for (yIn = 0; yIn < theHeight; ++yIn)
    for (xIn = 0; xIn < theWidth; ++xIn)
      {
      pix = XGetPixel(imageIn, xIn, yIn);

      if (pix != background)
        {
        xOut = xIn << 1;
        yOut = yIn << 1;

        XPutPixel(imageOut, xOut, yOut, pix);
        XPutPixel(imageOut, xOut+1, yOut, pix);
        XPutPixel(imageOut, xOut, yOut+1, pix);
        XPutPixel(imageOut, xOut+1, yOut+1, pix);
        }
      }

  pen->PutImage(Surface(), imageOut, 0, 0, 0, 0, theWidth << 1, theHeight << 1);

  ExposeAll();

  XDestroyImage(imageIn);
  XDestroyImage(imageOut);

  cursor.PointerCursor(mainPlot->Wdgt());
  cursor.PointerCursor(Wdgt());

}       /* END DRAW */
 
/* END MAGNIFYCANVAS.CC */
