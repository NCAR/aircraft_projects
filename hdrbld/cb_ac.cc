#include "hdrbld.h"

#include <Xm/RowColumn.h>


/* -------------------------------------------------------------------- */
void SetAircraft(Widget w, XtPointer client, XtPointer call)
{
  Arg         args[2];
  XmString    name;

  strcpy(flightInfo.acraft, aircraft[(int)client]);

printf("SetAircraft: new ac = %s\n", flightInfo.acraft);

  SetDSMlist(flightInfo.acraft);
  SetPMSlocns(flightInfo.acraft);

  if (!w)
    {
    name = XmStringCreateLocalized(aircraft[(int)client]);
    XtSetArg(args[0], XmNlabelString, name);
    XtSetValues(XmOptionButtonGadget(acOpMenu), args, 1);
    XmStringFree(name);
    }
}

/* END SETSH.C */
