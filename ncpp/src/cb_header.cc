/*
-------------------------------------------------------------------------
OBJECT NAME:	cb_header.cc

FULL NAME:	netCDF Header callbacks

ENTRY POINTS:	ViewHeader()
		DismissHeader()
		PrintHeader()

DESCRIPTION:	

REFERENCES:	none

REFERENCED BY:	Menu button.

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "Header.h"
#include "Application.h"
#include "FileMgr.h"

extern Application	*application;
extern FileManager	fileMgr;

static Header	*ncHeader = NULL;

/* -------------------------------------------------------------------- */
void DismissHeader(Widget w, XtPointer client, XtPointer call)
{
  delete ncHeader;
  ncHeader = NULL;

}	/* END DISMISSHEADER */

/* -------------------------------------------------------------------- */
void ViewHeader(Widget w, XtPointer client, XtPointer call)
{
  if (fileMgr.NumberOfFiles() == 0)
    return;

  if (ncHeader)
    delete ncHeader;

  ncHeader = new Header(application->Shell(), fileMgr.CurrentFile()->FileName());

}	/* END VIEWHEADER */

/* -------------------------------------------------------------------- */
void PrintHeader(Widget w, XtPointer client, XtPointer call)
{
  ncHeader->Print();

}	/* END PRINTHEADER */

/* END CB_HEADER.CC */
