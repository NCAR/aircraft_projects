/*
-------------------------------------------------------------------------
OBJECT NAME:	cb_mag.cc

FULL NAME:	Callback Wrappers for the magnify canvas.

ENTRY POINTS:	MagnifyExpose()
		MagnifyInput()
		MagnifyResize()

STATIC FNS:	

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	XtAppMainLoop()

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "define.h"

#include "MagnifyCanvas.h"

extern MagnifyCanvas	*magPlot;


/* -------------------------------------------------------------------- */
void MagnifyExpose(Widget w, XtPointer client, XtPointer call)
{
  magPlot->ExposeArea((XmDrawingAreaCallbackStruct *)call);

}	/* END MAGNIFYEXPOSE */

/* -------------------------------------------------------------------- */
void MagnifyResize(Widget w, XtPointer client, XtPointer call)
{
  magPlot->Resize();
  PageCurrent();

}	/* END MAGNIFYRESIZE */

/* -------------------------------------------------------------------- */
void MagnifyInput(Widget w, XtPointer client, XtPointer call)
{
  XmDrawingAreaCallbackStruct	*evt;
  XAnyEvent	*xe;

  evt = (XmDrawingAreaCallbackStruct *)call;
  xe = (XAnyEvent *)evt->event;
 
}	/* END MAGNIFYINPUT */

/* END CB_MAG.CC */
