/*
-------------------------------------------------------------------------
OBJECT NAME:	CanvasWindow.cc

FULL NAME:	

ENTRY POINTS:	CanvasWindow()

STATIC FNS:	

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-8
-------------------------------------------------------------------------
*/

#include "CanvasWindow.h"

struct menu
	{
	char            *title;
	void            (*callback)(Widget, XtPointer, XtPointer);
	XtPointer       callData;
	} ;
 
static struct menu	fileMenu[] = {
	{ "newFile", GetDataFileName, (XtPointer)NewDataFile, },
	{ "addFile", GetDataFileName, (XtPointer)AddDataFile, },
//	{ "separator", NULL, NULL, },
//	{ "Generate File", GetDataFileName, (XtPointer)GenerateFile, },
	{ "separator", NULL, NULL, },
	{ "printSetup", EditPrintParms, NULL, },
	{ "savePS", PrintSave, (XtPointer)1, },
	{ "print", PrintSave, NULL, },
#ifdef PNG
	{ "separator", NULL, NULL, },
	{ "savePNG", SavePNG, NULL, },
#endif
	{ "separator", NULL, NULL, },
	{ "quit", Quit, NULL, },
	{ NULL, NULL, NULL }};
 
static struct menu	legendMenu[] = {
	{ "editXYparms", EditParms, (void *)XY, },
	{ "editDiams", EditDiams, (void *)NULL, },
	{ NULL, NULL, NULL }};

static struct menu	viewMenu[] = {
	{ "viewASCII", ViewASCII, NULL, },
	{ "viewVars", ViewVars, NULL, },
	{ "viewTitles", ViewTitles, NULL, },
	{ "viewHeader", ViewHeader, NULL, },
	{ NULL, NULL, NULL }};

static struct menu	helpMenu[] = {
        { "RAF Homepage", ForkNetscape, (XtPointer)1 },
        { "RAF Software Page", ForkNetscape, (XtPointer)2 },
        { "ncpp User's Manual", ForkNetscape, (XtPointer)3 },
	{ NULL, NULL, NULL }};

static struct
	{
	char		*title;
	struct menu	*sub;
	} main_menu[] = {
		{ "File", fileMenu, },
		{ "Edit", legendMenu, },
		{ "View", viewMenu, },
		{ "Help", helpMenu, },
		{ NULL, NULL }};
 

/* -------------------------------------------------------------------- */
CanvasWindow::CanvasWindow(const Widget parent) : WinForm(parent, "canvas", Form)
{
  int		i, j;
  Cardinal	n;
  Arg		args[8];
  Widget	menubar, menu[5], bttn[16], menu_button[5];

  n = 0;
  menubar = XmCreateMenuBar(Window(), "menuBar", args, n);
  XtManageChild(menubar);

  for (i = 0; main_menu[i].title; ++i)
    {
    n = 0;
    menu[i] = XmCreatePulldownMenu(menubar, main_menu[i].title, args, n);
 
    n = 0;
    XtSetArg(args[n], XmNsubMenuId, menu[i]); ++n;
    menu_button[i] = XmCreateCascadeButton(menubar, main_menu[i].title, args,n);
 
    for (j = 0; main_menu[i].sub[j].title; ++j)
      {
      n = 0;
 
      if (main_menu[i].sub[j].callback == NULL)
        {
        bttn[j] = XmCreateSeparator(menu[i], main_menu[i].sub[j].title, args,n);
        continue;
        }
 
      bttn[j] = XmCreatePushButton(menu[i], main_menu[i].sub[j].title, args, n);
      XtAddCallback(bttn[j], XmNactivateCallback,
        main_menu[i].sub[j].callback, (void *)main_menu[i].sub[j].callData);
      }
 
    XtManageChildren(bttn, j);
    }
 
  XtManageChildren(menu_button, i);



  /* Create Graphics Canvas
   */
  n = 0;
  XtSetArg(args[n], XmNtopAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNbottomAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNleftAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNrightAttachment, XmATTACH_FORM); n++;
  drawA = XmCreateDrawingArea(Window(), "canvas", args, n);
 
  XtAddCallback(drawA, XmNexposeCallback, (XtCallbackProc)CanvasExpose, NULL);
  XtAddCallback(drawA, XmNinputCallback, (XtCallbackProc)CanvasInput, NULL);
  XtAddCallback(drawA, XmNresizeCallback, (XtCallbackProc)CanvasResize, NULL);

  XtManageChild(drawA);

}	/* END CONSTRUCTOR */

/* END CANVASWINDOW.CC */
