/*
-------------------------------------------------------------------------
OBJECT NAME:	cb_canvas.cc

FULL NAME:	Callback Wrappers for the main canvas.

ENTRY POINTS:	CanvasExpose()
		CanvasInput()
		CanvasResize()
		DoTheBox()

STATIC FNS:	

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	XtAppMainLoop()

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "define.h"

#include "MainCanvas.h"
#include "Magnify.h"

extern MainCanvas	*mainPlot;
extern Magnify		*mag;


/* -------------------------------------------------------------------- */
void CanvasExpose(Widget w, XtPointer client, XtPointer call)
{
  mainPlot->ExposeArea((XmDrawingAreaCallbackStruct *)call);

}	/* END CANVASEXPOSE */

/* -------------------------------------------------------------------- */
void CanvasResize(Widget w, XtPointer client, XtPointer call)
{
  mainPlot->Resize();
  PageCurrent();

}	/* END CANVASRESIZE */

/* -------------------------------------------------------------------- */
void CanvasInput(Widget w, XtPointer client, XtPointer call)
{
  XmDrawingAreaCallbackStruct	*evt;
  XAnyEvent	*xe;

  evt = (XmDrawingAreaCallbackStruct *)call;
  xe = (XAnyEvent *)evt->event;
 
  if (xe->type == 4 || xe->type == 5)
    mag->ProcessInput(evt);
 
}	/* END CANVASINPUT */

/* -------------------------------------------------------------------- */
void DoTheBox(Widget w, XtPointer client, XMotionEvent *evt, Boolean cont2disp)
{
  if (evt)
    mag->DrawBox(evt);
 
}       /* END DOTHEBOX */

/* END CB_CANVAS.CC */
