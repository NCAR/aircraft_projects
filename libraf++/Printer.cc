/*
-------------------------------------------------------------------------
OBJECT NAME:	Printer.cc

FULL NAME:	

ENTRY POINTS:	PopUp()
		SetShape()
		ApplyParms()

STATIC FNS:	

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "Printer.h"

#include <algorithm>
#include <cstdio>
#include <string>

using namespace std;


void	EditPrintParms(Widget w, XtPointer client, XtPointer call),
	ApplyPrintParms(Widget w, XtPointer client, XtPointer call),
	DismissWindow(Widget w, XtPointer client, XtPointer call);

void	ValidateTime(Widget w, XtPointer client, XtPointer call),
	ValidateFloat(Widget w, XtPointer client, XtPointer call),
	ValidateInteger(Widget w, XtPointer client, XtPointer call);

int	GetTextInt(const Widget w);
float	GetTextFloat(const Widget w);
void	GetTextString(const Widget w, string& s);
void	SetPrinterName(Widget w, XtPointer client, XtPointer call);


/* -------------------------------------------------------------------- */
Printer::Printer(Widget parent) : WinForm(parent, "print", RowColumn)
{
  Widget	plRC[TOTAL_PARMS], label, b[3], frame[5], RC[5],
		slPD, slOpMenu, slButts[MAX_PRINTERS];
  Arg		args[10];
  XmString	name;
  int		i, n, cnt;
  char		buffer[128];


  n = 0;
  frame[0] = XmCreateFrame(Window(), "printParmsFrame", args, 0);
  frame[1] = XmCreateFrame(Window(), "shapeFrame", args, 0);
  frame[2] = XmCreateFrame(Window(), "colorFrame", args, 0);
  frame[3] = XmCreateFrame(Window(), "buttonFrame", args, 0);
  XtManageChildren(frame, 4);

  n = 0;
  RC[0] = XmCreateRowColumn(frame[0], "printParmsRC", args, 0);
  RC[1] = XmCreateRadioBox(frame[1], "plRC", args, 0);
  RC[2] = XmCreateRadioBox(frame[2], "plRC", args, 0);
  RC[3] = XmCreateRowColumn(frame[3], "buttonRC", args, 0);
  XtManageChild(RC[0]); XtManageChild(RC[1]);
  XtManageChild(RC[2]); XtManageChild(RC[3]);


  /* Printer Op Menu
   */
  GetPrinterList();

  n = 0;
  slPD = XmCreatePulldownMenu(RC[0], "slPullDown", args, n);

  n = 0;
  XtSetArg(args[n], XmNsubMenuId, slPD); ++n;
  slOpMenu = XmCreateOptionMenu(RC[0], "prOpMenu", args, n);
  XtManageChild(slOpMenu);


  for (i = 0; printer_list[i]; ++i)
    {
    name = XmStringCreateLocalized(printer_list[i]);

    n = 0;
    XtSetArg(args[n], XmNlabelString, name); ++n;
    slButts[i] = XmCreatePushButton(slPD, "opMenB", args, n);
    XtAddCallback(slButts[i], XmNactivateCallback, SetPrinterName,
                  (XtPointer)printer_list[i]);

    XmStringFree(name);
    }

  XtManageChildren(slButts, i);


  /* Plot Parameters.
   */
  for (i = cnt = 0; i < TOTAL_PARMS; ++i, ++cnt)
    {
    n = 0;
    plRC[i] = XmCreateRowColumn(RC[0], "plRC", args, n);

    n = 0;
    sprintf(buffer, "lbl%d", cnt);
    label = XmCreateLabel(plRC[i], buffer, args, n);

    n = 0;
    sprintf(buffer, "txt%d", cnt);
    parmsText[cnt] = XmCreateTextField(plRC[i], buffer, args, n);

    XtManageChild(label);
    XtManageChild(parmsText[cnt]);

    if (i == 1 || i == 2)
      {
      XtAddCallback(parmsText[cnt],XmNlosingFocusCallback, ValidateFloat,
		(void *)"%.3f");

      label = XmCreateLabel(plRC[i], "inches", NULL, 0);
      XtManageChild(label);
      }
    }

  XtManageChildren(plRC, TOTAL_PARMS);


  n = 0;
  shapeB[0] = XmCreateToggleButton(RC[1], "Portrait", args, n);
  shapeB[1] = XmCreateToggleButton(RC[1], "Landscape", args, n);
  XtManageChildren(shapeB, 2);

  n = 0;
  colorB[0] = XmCreateToggleButton(RC[2], "Color", args, n);
  colorB[1] = XmCreateToggleButton(RC[2], "Black & White", args, n);
  XtManageChildren(colorB, 2);
  XmToggleButtonSetState(colorB[1], true, false);

  /* Command buttons.
   */
  n = 0;
  b[0] = XmCreatePushButton(RC[3], "applyButton", args, n);
  b[1] = XmCreatePushButton(RC[3], "resetButton", args, n);
  b[2] = XmCreatePushButton(RC[3], "dismissButton", args, n);
  XtAddCallback(b[0], XmNactivateCallback, ApplyPrintParms, NULL);
  XtAddCallback(b[1], XmNactivateCallback, EditPrintParms, NULL);
  XtAddCallback(b[2], XmNactivateCallback, DismissWindow, Window());
  XtManageChildren(b, 3);
 

#ifdef SVR4
  strcpy(lp_command, "lp -o nobanner");
#else
  strcpy(lp_command, "lpr -h");
#endif
  width = 11.0;
  height = 8.5;
  shape = LANDSCAPE;
  color = false;
  lineWidth = 1;

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void Printer::setParms()
{
  char	buffer[128];

  XmTextFieldSetString(parmsText[0], lpCommand());

  sprintf(buffer, "%.3f", width);
  XmTextFieldSetString(parmsText[1], buffer);

  sprintf(buffer, "%.3f", height);
  XmTextFieldSetString(parmsText[2], buffer);
 
  switch (shape)
    {
    case LANDSCAPE:
      XmToggleButtonSetState(shapeB[0], false, false);
      XmToggleButtonSetState(shapeB[1], true, false);
      break;
 
    case PORTRAIT:
      XmToggleButtonSetState(shapeB[0], true, false);
      XmToggleButtonSetState(shapeB[1], false, false);
      break;
    }

  XmToggleButtonSetState(colorB[0], color, false);
  XmToggleButtonSetState(colorB[1], !color, false);

}	/* END SETPARMS */

/* -------------------------------------------------------------------- */
void Printer::PopUp()
{
  setParms();
  WinForm::PopUp();

}	/* END POPUP */

/* -------------------------------------------------------------------- */
void Printer::SetPrinter(char *newPrinter)
{
  char  *p;

#ifdef SVR4
  p = strstr(lp_command, "-d");
#else
  p = strstr(lp_command, "-P");
#endif


  if (p)
    p[-1] = '\0';

  if (strcmp(newPrinter, "Default"))
    {
#ifdef SVR4
    strcat(lp_command, " -d ");
#else
    strcat(lp_command, " -P ");
#endif
    strcat(lp_command, newPrinter);
    }

  setParms();

}	/* END SETPRINTER */

/* -------------------------------------------------------------------- */
void Printer::SetShape(layout newShape)
{
  if (shape != newShape) // swap width & height.
    {
    float	tmp = width;

    width = height;
    height = tmp;
    
    shape = newShape;
    }
 
  setParms();

}	/* END SETSHAPE */

/* -------------------------------------------------------------------- */
float Printer::FontRatio()
{
  return(max((float)(HeightRatio() + WidthRatio()) / 2, (float)0.6));
}

/* -------------------------------------------------------------------- */
void Printer::ApplyParms()
{
  string	tmp;

  GetTextString(parmsText[0], tmp);
  strcpy(lp_command, tmp.c_str());

  width = GetTextFloat(parmsText[1]);
  height = GetTextFloat(parmsText[2]);

  if (XmToggleButtonGetState(shapeB[0]))
    shape = PORTRAIT;
  else
    shape = LANDSCAPE;

  if (XmToggleButtonGetState(colorB[0]))
    color = true;
  else
    color = false;

}	/* END APPLYPARMS */

/* -------------------------------------------------------------------- */
void Printer::GetPrinterList()
{
  FILE  *in;
  char  *p;
  int   i;
  char	buffer[256];

  memset(printer_list, 0, sizeof(printer_list));

  fprintf(stderr, "Detecting network printers....");

  if ((in = popen("lpstat -v", "r")) == NULL)
    {
    fprintf(stderr, "lpstat command failed.\n");
    return;
    }

  printer_list[0] = new char [8];
  strcpy(printer_list[0], "Default");

  for (i = 1; fgets(buffer, 256, in) > 0; ++i)
    {
    if (i >= MAX_PRINTERS-1)
      {
      fprintf(stderr, "\nGetPrinterList: Maximum number of printers reached, list will be incomplete.\n");
      break;
      }

    p = strtok(buffer, " ");
    p = strtok(NULL, " ");
    p = strtok(NULL, ":");

    printer_list[i] = new char [strlen(p)+1];
    strcpy(printer_list[i], p);
    }

  pclose(in);
  fprintf(stderr, "\n");

}       /* END GETPRINTERLIST */

/* END PRINTER.CC */
