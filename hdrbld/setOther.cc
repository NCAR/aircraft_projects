/*
-------------------------------------------------------------------------
OBJECT NAME:	setOther.c

FULL NAME:	

ENTRY POINTS:	SetOther()
		SetAsync()

STATIC FNS:	none

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2000
-------------------------------------------------------------------------
*/

#include "hdrbld.h"
#include "hardwire.h"


/* -------------------------------------------------------------------- */
void SetOther(Widget w, XtPointer client, XmToggleButtonCallbackStruct *call)
{
  int	index = ((int)client & 0xff00) >> 8,
	index1 = (int)client & 0xff;

  XtSetSensitive(other[index].DSMom[index1], call->set);

}

/* -------------------------------------------------------------------- */
void SetAsync(Widget w, XtPointer client, XmToggleButtonCallbackStruct *call)
{

}

/* END SETOTHER.C */
