/*
-------------------------------------------------------------------------
OBJECT NAME:	Window.cc

FULL NAME:	

ENTRY POINTS:	Window()
		PopUp()
		PopDown()

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "Window.h"


/* -------------------------------------------------------------------- */
WinForm::WinForm(Widget parent, char name[], winType wt)
{
  char		buff[32];

  strcpy(buff, name); strcat(buff, "Shell");
  shell = XtCreatePopupShell(buff, topLevelShellWidgetClass, parent, NULL, 0);

  strcpy(buff, name);

  if (wt == RowColumn)
    {
    strcat(buff, "RC");
    window = XmCreateRowColumn(shell, buff, NULL, 0);
    }
  else
    {
    strcat(buff, "Form");
    window = XmCreateForm(shell, buff, NULL, 0);
    }
 
}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
WinForm::~WinForm()
{
  PopDown();
  XtDestroyWidget(shell);

}	/* END DESTRUCTOR */

/* -------------------------------------------------------------------- */
void WinForm::PopUp() const
{
  XtManageChild(window);
  XtPopup(XtParent(window), XtGrabNone);

}	/* END POPUP */

/* -------------------------------------------------------------------- */
void WinForm::PopDown() const
{
  XtPopdown(XtParent(window));
  XtUnmanageChild(window);

}	/* END POPDOWN */

/* -------------------------------------------------------------------- */
void WinForm::SetPosition(int x, int y) const
{
  Cardinal	n;
  Arg		args[2];

  n = 0;
  XtSetArg(args[n], XmNx, x); ++n;
  XtSetArg(args[n], XmNy, y); ++n;
  XtSetValues(shell, args, n);

}	/* END SETPOSITION */

/* END WINDOW.CC */
