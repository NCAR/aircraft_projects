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

#include "Canvas.h"
#include "PlotMgr.h"

extern Canvas		*mainCanvas;
extern PlotManager	*plotMgr;


/* -------------------------------------------------------------------- */
void CanvasExpose(Widget w, XtPointer client, XtPointer call)
{
  mainCanvas->ExposeArea((XmDrawingAreaCallbackStruct *)call);

}	/* END CANVASEXPOSE */

/* -------------------------------------------------------------------- */
void CanvasResize(Widget w, XtPointer client, XtPointer call)
{
  mainCanvas->Resize();
  plotMgr->Resize();
  plotMgr->DrawImage();

}	/* END CANVASRESIZE */

/* -------------------------------------------------------------------- */
void CanvasInput(Widget w, XtPointer client, XtPointer call)
{
  XmDrawingAreaCallbackStruct	*evt;
  XAnyEvent	*xe;

  evt = (XmDrawingAreaCallbackStruct *)call;
  xe = (XAnyEvent *)evt->event;
 
  if (xe->type == 4 || xe->type == 5)
    ;
 
}	/* END CANVASINPUT */

/* -------------------------------------------------------------------- */
void DoTheBox(Widget w, XtPointer client, XMotionEvent *evt, Boolean cont2disp)
{
  if (evt)
    ;
 
}       /* END DOTHEBOX */

/* END CB_CANVAS.CC */
