/*
-------------------------------------------------------------------------
OBJECT NAME:	Magnify.cc

FULL NAME:	Magnify box control

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "Magnify.h"
#include "Colors.h"
#include "XPen.h"
#include "MainCanvas.h"
#include "MagnifyWindow.h"
#include "MagnifyCanvas.h"

void DoTheBox(Widget w, XtPointer client, XMotionEvent *evt, Boolean cont2disp);

extern Colors		*color;
extern MainCanvas	*mainPlot;
extern MagnifyWindow	*magWindow;
extern MagnifyCanvas	*magPlot;
extern XPen		*pen;


/* -------------------------------------------------------------------- */
Magnify::Magnify()
{
  startX = startY = endX = endY = 0;
  width = height = 0;

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void Magnify::ProcessInput(XmDrawingAreaCallbackStruct *evt)
{
  XButtonEvent  *xb = (XButtonEvent *)evt->event;
  static bool   cancel = false;
 
  if (xb->button != Button1)
    return;
 
  if (xb->state == 0)
    startX = startY = endX = endY = 0;
 
  if (xb->state == 0x100)
    {
    XtRemoveEventHandler(mainPlot->Wdgt(), Button1MotionMask, False,
                         (XtEventHandler)DoTheBox, NULL);
    RemoveBox();
    pen->SetFunction(GXcopy);
    }
 
  if (xb->state != 0)
    if (cancel || endX < startX || endY < startY)
      return;
 
  if (xb->state == 0)
    {
    cancel = false;
 
    startX = xb->x;
    startY = xb->y;
 
    pen->SetColor(color->GetColor(2));
    pen->SetLineWidth(1);
    pen->SetFunction(GXxor);
    XtAddEventHandler(mainPlot->Wdgt(), Button1MotionMask, False,
                      (XtEventHandler)DoTheBox, NULL);
    }
  else if (xb->state == 0x100)
    {
    if (abs(startX - xb->x) < 10 || abs(startY - xb->y) < 10)
      return;
 
    endX = xb->x;
    endY = xb->y;

    width = endX - startX;
    height = endY - startY;

    magWindow->PopUp();

    if (magPlot == NULL)
      magPlot = new MagnifyCanvas(magWindow->DrawingArea());

    magPlot->draw();
    }

}	/* END MAGNIFY */

/* -------------------------------------------------------------------- */
void Magnify::DrawBox(XMotionEvent *evt)
{
  pen->SetColor(color->GetColor(2));
  pen->SetLineWidth(1);
 
  if (endX != 0 && endY != 0)
    pen->DrawRectangle(mainPlot->Surface(),
		startX, startY, endX - startX, endY - startY);
 
  endX = evt->x;
  endY = evt->y;
 
  pen->DrawRectangle(mainPlot->Surface(),
		startX, startY, endX - startX, endY - startY);

}	/* END DRAWBOX */

/* -------------------------------------------------------------------- */
void Magnify::RemoveBox()
{
  if (endX != 0 && endY != 0)
    pen->DrawRectangle(mainPlot->Surface(),
                   startX, startY, endX - startX, endY - startY);
 
}	/* END REMOVEBOX */

/* END MAGNIFY.CC */
