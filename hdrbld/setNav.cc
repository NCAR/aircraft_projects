/*
-------------------------------------------------------------------------
OBJECT NAME:	setNav.c

FULL NAME:	

ENTRY POINTS:	

STATIC FNS:	none

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1996
-------------------------------------------------------------------------
*/

#include "hdrbld.h"
#include "hardwire.h"

#include <Xm/RowColumn.h>

/* Every function in here needs these vars, and I'm too lazy to type them
 * over and over.
 */
static Arg	args[2];
static XmString	name;

/* -------------------------------------------------------------------- */
void SetPrimaryInertial(Widget w, XtPointer client, XtPointer call)
{
  Inertial[0] = (int)client;

  if (Inertial[0])
    {
    XtSetSensitive(navDSMom[1], TRUE);
    XtSetSensitive(navTypeOM[1], TRUE);
    }
  else
    {
    XtSetSensitive(navDSMom[1], FALSE);
    XtSetSensitive(navTypeOM[1], FALSE);
    }

  if (!w) /* If this is being called from cb_file  */
    {
    name = XmStringCreateLocalized(inertial[Inertial[0]].longName);
    XtSetArg(args[0], XmNlabelString, name);
    XtSetValues(XmOptionButtonGadget(navTypeOM[0]), args, 1);
    XmStringFree(name);
    }
  else
    {
    if (client)
      AddToChangeLog("Primary IRU added.\n");
    else
      AddToChangeLog("Primary IRU deleted.\n");
    }
}

/* -------------------------------------------------------------------- */
void SetSecondaryInertial(Widget w, XtPointer client, XtPointer call)
{
  Inertial[1] = (int)client;

  if (!w) /* If this is being called from EditVariable()  */
    {
    name = XmStringCreateLocalized(inertial[Inertial[1]].longName);
    XtSetArg(args[0], XmNlabelString, name);
    XtSetValues(XmOptionButtonGadget(navTypeOM[1]), args, 1);
    XmStringFree(name);
    }
  else
    {
    if (client)
      AddToChangeLog("Secondary IRU added.\n");
    else
      AddToChangeLog("Secondary IRU deleted.\n");
    }
}

/* -------------------------------------------------------------------- */
void SetPrimaryGPS(Widget w, XtPointer client, XtPointer call)
{
  GPS[0] = (int)client;

  if (GPS[0])
    {
    XtSetSensitive(navDSMom[3], TRUE);
    XtSetSensitive(navTypeOM[3], TRUE);
    }
  else
    {
    XtSetSensitive(navDSMom[3], FALSE);
    XtSetSensitive(navTypeOM[3], FALSE);
    XtSetSensitive(navDSMom[4], FALSE);
    XtSetSensitive(navTypeOM[4], FALSE);
    }

  if (!w) /* If this is being called from EditVariable()  */
    {
    name = XmStringCreateLocalized(gps[GPS[0]].longName);
    XtSetArg(args[0], XmNlabelString, name);
    XtSetValues(XmOptionButtonGadget(navTypeOM[2]), args, 1);
    XmStringFree(name);
    }
  else
    {
    if (client)
      AddToChangeLog("Primary GPS added/changed.\n");
    else
      AddToChangeLog("Primary GPS deleted.\n");
    }
}

/* -------------------------------------------------------------------- */
void SetSecondaryGPS(Widget w, XtPointer client, XtPointer call)
{
  GPS[1] = (int)client;

  if (GPS[1])
    {
    XtSetSensitive(navDSMom[4], TRUE);
    XtSetSensitive(navTypeOM[4], TRUE);
    }
  else
    {
    XtSetSensitive(navDSMom[4], FALSE);
    XtSetSensitive(navTypeOM[4], FALSE);
    }

  if (!w) /* If this is being called from EditVariable()  */
    {
    name = XmStringCreateLocalized(gps[GPS[1]].longName);
    XtSetArg(args[0], XmNlabelString, name);
    XtSetValues(XmOptionButtonGadget(navTypeOM[3]), args, 1);
    XmStringFree(name);
    }
  else
    {
    if (client)
      AddToChangeLog("Second GPS added/changed.\n");
    else
      AddToChangeLog("Second GPS deleted.\n");
    }
}

/* -------------------------------------------------------------------- */
void SetTertiaryGPS(Widget w, XtPointer client, XtPointer call)
{
  GPS[2] = (int)client;

  if (!w) /* If this is being called from EditVariable()  */
    {
    name = XmStringCreateLocalized(gps[GPS[2]].longName);
    XtSetArg(args[0], XmNlabelString, name);
    XtSetValues(XmOptionButtonGadget(navTypeOM[4]), args, 1);
    XmStringFree(name);
    }
  else
    {
    if (client)
      AddToChangeLog("Third GPS added/changed.\n");
    else
      AddToChangeLog("Third GPS deleted.\n");
    }
}

/* END SETNAV.C */
