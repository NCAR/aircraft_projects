#include "hdrbld.h"
#include "hardwire.h"

#include <Xm/RowColumn.h>
#include <Xm/TextF.h>


/* -------------------------------------------------------------------- */
void ClearCurrentSh(Widget w, XtPointer client, XtPointer call)
{
  int		i;

  memset((char *)&currentSh, 0, sizeof(Sh));

  strcpy(currentSh.item_type, SDI_STR);
  currentSh.item_len = sizeof(Sh);
  strcpy(currentSh.type, typeListChar[0]);
  currentSh.length = sizeof(short);
  currentSh.convert = 0.0;
  currentSh.convert_offset = 0;
  currentSh.order = 2;
  currentSh.cof[0] = 0.0;
  currentSh.cof[1] = 1.0;

  XmTextFieldSetString(varText, "");
  SetSDI_DSM(NULL, (XtPointer)0, NULL);
  SetSDI_Type(NULL, (XtPointer)0, NULL);
  SetSDI_SampleRate(NULL, (XtPointer)2, NULL);
  SetSDI_CardAddr(NULL, (XtPointer)0, NULL);
  SetSDI_Gain(NULL, (XtPointer)0, NULL);
  SetSDI_Offset(NULL, (XtPointer)0, NULL);

  for (i = 0; i < MX_COF; ++i)
    {
    if (i < currentSh.order)
      {
      sprintf(buffer, "%e", currentSh.cof[i]);
      XmTextFieldSetString(calText[i], buffer);
      }
    else
      XmTextFieldSetString(calText[i], "");
    }
}

/* -------------------------------------------------------------------- */
void SetSDI_DSM(Widget w, XtPointer client, XtPointer call)
{
  strcpy(currentSh.dsm_locn, DSM[(int)client]);

  if (!w) /* If this is being called from EditVariable()  */
    SetMenu(SDIom[0], DSM[(int)client]);
}

/* -------------------------------------------------------------------- */
void SetSDI_Type(Widget w, XtPointer client, XtPointer call)
{
  Arg         args[2];
  XmString    name;

  strcpy(currentSh.type, typeListChar[(int)client]);

  if (!w) /* If this is being called from EditVariable()  */
    {
    name = XmStringCreateLocalized(typeList[(int)client]);
    XtSetArg(args[0], XmNlabelString, name);
    XtSetValues(XmOptionButtonGadget(SDIom[1]), args, 1);
    XmStringFree(name);
    }

  switch ((int)client)
    {
    case 0:		/* Analog		*/
      strcpy(currentSh.item_type, SDI_STR);
      XtSetSensitive(SDIom[4], TRUE);
      XtSetSensitive(SDIom[5], TRUE);
      XtSetSensitive(gainButts[1], TRUE);
      XtSetSensitive(gainButts[2], TRUE);
      XtSetSensitive(gainButts[3], FALSE);
      XtSetSensitive(gainButts[4], TRUE);
      XtSetSensitive(srButts[0], FALSE);
      XtSetSensitive(srButts[3], FALSE);
      XtSetSensitive(srButts[4], FALSE);
      XtSetSensitive(srButts[5], TRUE);
      XtSetSensitive(srButts[6], TRUE);
      XtSetSensitive(srButts[7], TRUE);
      break;

    case 1:		/* Digital		*/
    case 2:		/* Digital Out	*/
    case 3:		/* Counter		*/
      strcpy(currentSh.item_type, SDI_STR);

      XtSetSensitive(SDIom[4], FALSE);
      XtSetSensitive(SDIom[5], FALSE);
      XtSetSensitive(srButts[0], TRUE);
      XtSetSensitive(srButts[1], TRUE);
      XtSetSensitive(srButts[2], TRUE);
      XtSetSensitive(srButts[3], TRUE);
      XtSetSensitive(srButts[4], TRUE);
      XtSetSensitive(srButts[5], FALSE);
      XtSetSensitive(srButts[6], FALSE);
      XtSetSensitive(srButts[7], FALSE);
      break;

    case 4:		/* AUX Analog	*/
      strcpy(currentSh.item_type, SDI_STR);
      XtSetSensitive(SDIom[4], TRUE);
      XtSetSensitive(SDIom[5], FALSE);
      XtSetSensitive(gainButts[1], FALSE);
      XtSetSensitive(gainButts[2], FALSE);
      XtSetSensitive(gainButts[3], TRUE);
      XtSetSensitive(gainButts[4], FALSE);
      XtSetSensitive(srButts[0], FALSE);
      XtSetSensitive(srButts[3], FALSE);
      XtSetSensitive(srButts[4], FALSE);
      XtSetSensitive(srButts[5], FALSE);
      XtSetSensitive(srButts[6], FALSE);
      XtSetSensitive(srButts[7], FALSE);
      break;
    }
}

/* -------------------------------------------------------------------- */
void SetSDI_SampleRate(Widget w, XtPointer client, XtPointer call)
{
  Arg         args[2];
  XmString    name;

  currentSh.rate = atoi(sampleRates[(int)client]);

  if (!w) /* If this is being called from EditVariable()  */
    {
    name = XmStringCreateLocalized(sampleRates[(int)client]);
    XtSetArg(args[0], XmNlabelString, name);
    XtSetValues(XmOptionButtonGadget(SDIom[2]), args, 1);
    XmStringFree(name);
    }
}

/* -------------------------------------------------------------------- */
void SetSDI_CardAddr(Widget w, XtPointer client, XtPointer call)
{
  Arg         args[2];
  XmString    name;

  currentSh.adsaddr = (int)client;

  if (!w) /* If this is being called from EditVariable()  */
    {
    sprintf(buffer, "%x", (int)client);
    name = XmStringCreateLocalized(buffer);
    XtSetArg(args[0], XmNlabelString, name);
    XtSetValues(XmOptionButtonGadget(SDIom[3]), args, 1);
    XmStringFree(name);
    }
}

/* -------------------------------------------------------------------- */
void SetSDI_Gain(Widget w, XtPointer client, XtPointer call)
{
  Arg         args[2];
  XmString    name;

  currentSh.ch_gain = atoi(gains[(int)client]);

  if (!w) /* If this is being called from EditVariable()  */
    {
    name = XmStringCreateLocalized(gains[(int)client]);
    XtSetArg(args[0], XmNlabelString, name);
    XtSetValues(XmOptionButtonGadget(SDIom[4]), args, 1);
    XmStringFree(name);
    }
}

/* -------------------------------------------------------------------- */
void SetSDI_Offset(Widget w, XtPointer client, XtPointer call)
{
  Arg         args[2];
  XmString    name;

  currentSh.ch_offset = atoi(offsets[(int)client]);

  if (!w) /* If this is being called from EditVariable()  */
    {
    name = XmStringCreateLocalized(offsets[(int)client]);
    XtSetArg(args[0], XmNlabelString, name);
    XtSetValues(XmOptionButtonGadget(SDIom[5]), args, 1);
    XmStringFree(name);
    }
}
/* END SETSH.C */
