/*
-------------------------------------------------------------------------
OBJECT NAME:	cb_printer.cc

FULL NAME:	Callbacks to PrinterSetup

ENTRY POINTS:	EditPrintParms()
		ApplyPrintParms()
		SetPrinterName()

DESCRIPTION:	none

REFERENCES:	none

REFERENCED BY:	Menu button.

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-8
-------------------------------------------------------------------------
*/

#include "Printer.h"

extern Printer		*printerSetup;


/* -------------------------------------------------------------------- */
void EditPrintParms(Widget w, XtPointer client, XtPointer call)
{
  printerSetup->PopUp();

}	/* END EDITPRINTPARMS */

/* -------------------------------------------------------------------- */
void ApplyPrintParms(Widget w, XtPointer client, XtPointer call)
{
  printerSetup->ApplyParms();

}	/* END APPLYPRINTPARMS */

/* -------------------------------------------------------------------- */
void SetPrinterName(Widget w, XtPointer client, XtPointer call)
{
  printerSetup->SetPrinter((char *)client);

}	/* END SETPRINTERNAME */

/* END CB_PRINTER.CC */
