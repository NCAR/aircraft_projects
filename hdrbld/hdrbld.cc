/*
-------------------------------------------------------------------------
OBJECT NAME:	hdrbld.c

FULL NAME:	

ENTRY POINTS:	main()

STATIC FNS:	none

DESCRIPTION:	

INPUT:		

OUTPUT:		

REFERENCES:	Xwin.c, init.c then enters XtAppMainLoop()

REFERENCED BY:	user

COPYRIGHT:	University Corporation for Atmospheric Research, 1996-2001
-------------------------------------------------------------------------
*/

#include "hdrbld.h"
#include "fbr.h"

#include <Xm/Protocols.h>

#define APP_NAME	"hdrbld"
#define APP_CLASS	"XmHdrBld"


Widget	AppShell;			/* The Main Application Shell */
Widget	Shell000, MainWindow;
Widget	Shell001;

XtAppContext context;


Widget	CreateMainWindow(Widget parent);
void	CreateHDwindow(Widget parent), CreateEditWindow(Widget parent);
void	DismissEditWindow(Widget w, XtPointer client, XtPointer call);
void	Quit(Widget w, XtPointer client, XtPointer call);


/* -------------------------------------------------------------------- */
int main(int argc, char **argv)
{
  Arg		args[8];
  Cardinal	n;
  Atom		WM_DELETE_WINDOW;

  ProcessArgv(argc, argv);
  PreWidgetInitialize();

  n = 0;
  AppShell = XtAppInitialize(&context, APP_CLASS, NULL, 0, &argc, argv,
				fallback_resources, NULL, 0);

  WM_DELETE_WINDOW =
	XmInternAtom(XtDisplay(AppShell), "WM_DELETE_WINDOW", False);

  n = 0;
  Shell000 = XtCreatePopupShell("topLevelShell", 
				topLevelShellWidgetClass, AppShell, args, n);

  MainWindow = CreateMainWindow(Shell000);


  n = 0;
  Shell001 = XtCreatePopupShell("editShell", 
				topLevelShellWidgetClass, AppShell, args, n);

  CreateEditWindow(Shell001);


  XmAddWMProtocolCallback(Shell000, WM_DELETE_WINDOW, Quit, NULL);

// Currently causes core dump when you go to edit another file (re-manage
// window.
//  XmAddWMProtocolCallback(Shell001, WM_DELETE_WINDOW, DismissEditWindow, NULL);

  CreateErrorBox(AppShell);
  CreateQueryBox(AppShell);
  CreateWarningBox(AppShell);
  CreateFileSelectionBox(AppShell);


  XtManageChild(MainWindow);
  XtPopup(XtParent(MainWindow), XtGrabNone);

  PostWidgetInitialize();

  {
  /* Had to add this hack, because all of a sudden it refused to accept the
   * setting in fbr.h.
   */
  Arg args[2];
  XtSetArg(args[0], XmNwidth, 600);
  XtSetValues(varList, args, 1);
  }

  XtAppMainLoop(context);

  return(0);

}	/* END MAIN */

/* END HDRBLD.C */
