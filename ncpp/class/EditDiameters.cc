/*
-------------------------------------------------------------------------
OBJECT NAME:	EditDiameters.cc

FULL NAME:	

ENTRY POINTS:	

STATIC FNS:	

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1998-9
-------------------------------------------------------------------------
*/

#include "EditDiameters.h"


/* -------------------------------------------------------------------- */
EditDiameters::EditDiameters(const Widget parent) : WinForm(parent, "editDiams", RowColumn)
{
  int		i, j, k, nTxt;
  Cardinal	n;
  Arg		args[8];
  Widget	diamFrame, RC, probeRC, drFrame, drRC, b[3],
		plRC, innerRC;
  DataFile	*file;

  txtCnt = 0;

  n = 0;
  diamFrame = XmCreateFrame(Window(), "diamFrame", args, n);
  XtManageChild(diamFrame);

  n = 0;
  fileLabel = XmCreateLabel(diamFrame, "Select Probe", args, n);
  XtManageChild(fileLabel);

  n = 0;
  RC = XmCreateRowColumn(diamFrame, "diamRC", args, n);
  XtManageChild(RC);


  n = 0;
  probeRC = XmCreateRadioBox(RC, "probeRC", args, n);
  XtManageChild(probeRC);


  /* Probe Toggle Buttons.
   */
  for (int i = 0; i < MAX_PROBES; ++i)
    {
    n = 0;
    probeB[i] = XmCreateToggleButton(probeRC, "none      ", NULL, 0);
    XtAddCallback(probeB[i], XmNvalueChangedCallback,
                  (XtCallbackProc)SetDiams, (XtPointer)i);
    }

  XtManageChildren(probeB, MAX_PROBES);



  n = 0;
  drFrame = XmCreateFrame(RC, "drFrame", args, n);
  XtManageChild(drFrame);
  innerRC = XmCreateRowColumn(drFrame, "innerRC", args, n);
  XtManageChild(innerRC);
  plRC = XmCreateRowColumn(innerRC, "plRC", args, n);
  XtManageChild(plRC);

  n = 0;
  probeLabel = XmCreateLabel(plRC, "test", args, n);
  XtManageChild(probeLabel);

  n = 0;
  XtManageChild(XmCreateLabel(plRC, "Starting bin #", args, n));
  text[txtCnt] = XmCreateTextField(plRC, "startBin", args, n);
  XtManageChild(text[txtCnt++]);
  XtManageChild(XmCreateLabel(plRC, "Ending bin #", args, n));
  text[txtCnt] = XmCreateTextField(plRC, "startBin", args, n);
  XtManageChild(text[txtCnt++]);

  n = 0;
  for (; txtCnt < 6; ++txtCnt)
    {
    text[txtCnt] = XmCreateTextField(innerRC, "diamTxt", args, n);
    XtManageChild(text[txtCnt]);
    }

  n = 0;
  for (; txtCnt < 12; ++txtCnt)
    {
    plRC = XmCreateRowColumn(innerRC, "plRC", args, n);
    XtManageChild(plRC);

    miscLabel[txtCnt] = XmCreateLabel(plRC, "miscLabel", args, n);
    XtManageChild(miscLabel[txtCnt]);

    text[txtCnt] = XmCreateTextField(plRC, "miscTxt", args, n);
    XtManageChild(text[txtCnt]);
    }


  n = 0;
  drFrame = XmCreateFrame(Window(), "buttonFrame", args, n);
  XtManageChild(drFrame);

  n = 0;
  drRC = XmCreateRowColumn(drFrame, "buttonRC", args, n);
  XtManageChild(drRC);
 
  n = 0;
  b[0] = XmCreatePushButton(drRC, "applyButton", args, n);
 
  n = 0;
  b[1] = XmCreatePushButton(drRC, "resetButton", args, n);
 
  n = 0;
  b[2] = XmCreatePushButton(drRC, "dismissButton", args, n);
 
  XtManageChildren(b, 3);
 
  XtAddCallback(b[0],XmNactivateCallback, ApplyDiams, (XtPointer)NULL);
  XtAddCallback(b[1],XmNactivateCallback, SetDiams, (XtPointer)NULL);
  XtAddCallback(b[2],XmNactivateCallback, DismissWindow, (XtPointer)Window());

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void EditDiameters::SetProbeNames(DataFile *currFile)
{
  int	i;
  XmString      label;
  Arg           args[2];

  for (i = 0; i < currFile->NumberOfProbes(); ++i)
    {
    XtSetSensitive(probeB[i], True);

    label = XmStringCreate((char *)currFile->probe[i]->Name().c_str(),
					XmFONTLIST_DEFAULT_TAG);
    XtSetArg(args[0], XmNlabelString, label);
    XtSetValues(probeB[i], args, 1);
    XmStringFree(label);

    XmToggleButtonSetState(probeB[i], False, False);
    }

  for (; i < MAX_PROBES; ++i)
    {
    XtSetSensitive(probeB[i], False);

    label = XmStringCreate("none    ", XmFONTLIST_DEFAULT_TAG);
    XtSetArg(args[0], XmNlabelString, label);
    XtSetValues(probeB[i], args, 1);
    XmStringFree(label);

    XmToggleButtonSetState(probeB[i], False, False);
    }

  XmToggleButtonSetState(probeB[0], True, True);

}	/* END SETPROBENAMES */

/* -------------------------------------------------------------------- */
void EditDiameters::SetDiameters(Probe *probe)
{
  int	i, j, cnt, nTxt;
  Arg		args[1];
  XmString	label;

  label = XmStringCreate((char *)probe->Name().c_str(), XmFONTLIST_DEFAULT_TAG);
  XtSetArg(args[0], XmNlabelString, label);
  XtSetValues(probeLabel, args, 1);
  XmStringFree(label);

  cnt = 0;

  sprintf(buffer, "%d", probe->FirstBin());
  XmTextFieldSetString(text[cnt++], buffer);
  sprintf(buffer, "%d", probe->LastBin());
  XmTextFieldSetString(text[cnt++], buffer);

  nTxt = probe->VectorLength() / 16;
  if (probe->Type() == Probe::FSSP)
    nTxt *= 4;

  for (i = 0; i < nTxt+1; ++i)
    {
    buffer[0] = '\0';

    XtSetSensitive(text[cnt], True);

    for (j = 0; j < 16 && (i*16)+j < probe->VectorLength(); ++j)
      sprintf(&buffer[strlen(buffer)], "%5g ", probe->CellSize((i*16)+j));

    XmTextFieldSetString(text[cnt++], buffer);
    }

  for (; cnt < 6; ++cnt)
    {
    XtSetSensitive(text[cnt], False);
    XmTextFieldSetString(text[cnt], "");
    }

  cnt = 6;

  // Set up misc stuff.
  switch (probe->Type())
    {
    case Probe::FSSP:
      setSpex("DBZ Factor", cnt++, ((FSSP *)probe)->DBZfac);
      setSpex("Liquid Water Content Factor", cnt++, ((FSSP *)probe)->PLWfac);
      setSpex("Density of Water", cnt++, ((FSSP *)probe)->DENS);
      setSpex("Depth of Field", cnt++, ((FSSP *)probe)->DOF);
      setSpex("Beam Diameter", cnt++, ((FSSP *)probe)->beamDiameter);
      break;

    case Probe::X260:
    case Probe::TWODP:
    case Probe::TWODC:
      setSpex("DBZ Factor", cnt++, ((Probe200 *)probe)->DBZfac);

    case Probe::X200:
    case Probe::Y200:
      setSpex("Liquid Water Content Factor", cnt++,((Probe200 *)probe)->PLWfac);
      setSpex("Density of Water", cnt++, ((Probe200 *)probe)->DENS);
      setSpex("Number of Diodes", cnt++, (float)((Probe200 *)probe)->nDiodes);
      setSpex("Arm Distance", cnt++, ((Probe200 *)probe)->armDistance);
      setSpex("Response Time", cnt++, ((Probe200 *)probe)->responseTime);

      break;
    }

  for (; cnt < 12; ++cnt)
    {
    label = XmStringCreate("" , XmFONTLIST_DEFAULT_TAG);
    XtSetArg(args[0], XmNlabelString, label);
    XtSetValues(miscLabel[cnt], args, 1);
    XmStringFree(label);

    XtSetSensitive(text[cnt], False);
    XmTextFieldSetString(text[cnt], "");
    }


}	/* END SETDIAMETERS */

/* -------------------------------------------------------------------- */
void EditDiameters::ApplyDiameters(Probe *probe)
{
  int	i, j, k, l, cnt, nTxt, first, last;
  DataFile	*file;
  char		*p, *p1;
  float		cells[256];

  cnt = 0;

  first = GetTextInt(text[cnt++]);
  last = GetTextInt(text[cnt++]);

  nTxt = probe->VectorLength() / 16;
  if (probe->Type() == Probe::FSSP)
    nTxt *= 4;

  for (k = 0; k < nTxt; ++k)
    {
    p = XmTextFieldGetString(text[cnt++]);
    p1 = strtok(p, ", ");

    for (l = 0; l < 16; ++l)
      {
      cells[(k*16)+l] = atof(p1);
      p1 = strtok(NULL, ", ");
      }

    XtFree(p);
    }

  probe->UpdateCellDiams(first, last, cells);

  for (; cnt < 6; ++cnt)
    ;


  // Set up misc stuff.
  switch (probe->Type())
    {
    case Probe::FSSP:
      ((FSSP *)probe)->DBZfac = GetTextFloat(text[cnt++]);
      ((FSSP *)probe)->PLWfac = GetTextFloat(text[cnt++]);
      ((FSSP *)probe)->DENS = GetTextFloat(text[cnt++]);
      ((FSSP *)probe)->DOF = GetTextFloat(text[cnt++]);
      ((FSSP *)probe)->beamDiameter = GetTextFloat(text[cnt++]);
      break;

    case Probe::X260:
      ((Probe200 *)probe)->DBZfac = GetTextFloat(text[cnt++]);

    case Probe::X200:
    case Probe::Y200:
      ((Probe200 *)probe)->PLWfac = GetTextFloat(text[cnt++]);
      ((Probe200 *)probe)->DENS = GetTextFloat(text[cnt++]);
      ((Probe200 *)probe)->nDiodes = GetTextInt(text[cnt++]);
      ((Probe200 *)probe)->armDistance = GetTextFloat(text[cnt++]);
      ((Probe200 *)probe)->responseTime = GetTextFloat(text[cnt++]);
      break;
    }

}	/* END APPLYDIAMETERS */

/* -------------------------------------------------------------------- */
void EditDiameters::setSpex(char *labelTxt, int cnt, float value)
{
  XmString	label;
  Arg		args[2];
  char		buff[32];

  label = XmStringCreate(labelTxt, XmFONTLIST_DEFAULT_TAG);
  XtSetArg(args[0], XmNlabelString, label);
  XtSetValues(miscLabel[cnt], args, 1);
  XmStringFree(label);

  XtSetSensitive(text[cnt], True);
  sprintf(buff, "%g", value);
  XmTextFieldSetString(text[cnt], buff);

}	/* END SETSPEX */

/* END EDITDIAMETERS.CC */
