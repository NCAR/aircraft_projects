/*
-------------------------------------------------------------------------
OBJECT NAME:	TextWindow.cc

FULL NAME:	

ENTRY POINTS:	

STATIC FNS:	

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1998-2001
-------------------------------------------------------------------------
*/

#include "TextWindow.h"

#include <Xm/Frame.h>
#include <Xm/RowColumn.h>
#include <Xm/PushB.h>
#include <Xm/Text.h>
#include <Xm/TextF.h>


/* -------------------------------------------------------------------- */
TextWindow::TextWindow(const Widget parent, char name[]) : WinForm(parent, name, Form)
{
  int		i, j;
  Cardinal	n;
  Arg		args[8];
  Widget	drFrame, drRC, b[4];
  char		space[32];

  n = 0;
  XtSetArg(args[n], XmNtopAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNleftAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNrightAttachment, XmATTACH_FORM); n++;
  drFrame = XmCreateFrame(Window(), "buttonFrame", args, n);
  XtManageChild(drFrame);
 
  n = 0;
  drRC = XmCreateRowColumn(drFrame, "buttonRC", args, n);
  XtManageChild(drRC);
 
  n = 0;
  b[0] = XmCreatePushButton(drRC, "dismissButton", args, n);
  b[1] = XmCreatePushButton(drRC, "printButton", args, n);
  b[2] = XmCreatePushButton(drRC, "saveButton", args, n);
  b[3] = XmCreatePushButton(drRC, "searchButton", args, n);
 
  XtManageChildren(b, 4);
 
  n = 0;
  searchTxt = XmCreateTextField(drRC, "searchTxt", args, n);
  XtManageChild(searchTxt);

 
  n = 0;
  XtSetArg(args[n], XmNtopAttachment, XmATTACH_WIDGET); n++;
  XtSetArg(args[n], XmNtopWidget, drFrame); n++;
  XtSetArg(args[n], XmNleftAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNrightAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNbottomAttachment, XmATTACH_FORM); n++;

  strcpy(space, name); strcat(space, "Text");
  text = XmCreateScrolledText(Window(), space, args, n);
  XtManageChild(text);

  XtAddCallback(b[0], XmNactivateCallback, DismissText, this);
  XtAddCallback(b[1], XmNactivateCallback, PrintText, text);
  XtAddCallback(b[2], XmNactivateCallback, SaveText, text);
  XtAddCallback(b[3], XmNactivateCallback, SearchText, this);

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void TextWindow::Search()
{
  char	*target;
  int	len;
  bool	found;
  XmTextPosition	searchPos;
  static XmTextPosition	currPos = 0;

  len = XmTextGetLastPosition(text);
  XmTextSetHighlight(text, 0, len, XmHIGHLIGHT_NORMAL);

  target = XmTextFieldGetString(searchTxt);

  if ((len = strlen(target)) == 0)
    {
    XtFree(target);
    return;
    }


  currPos = 0;
  found = XmTextFindString(text, currPos, target, XmTEXT_FORWARD, &searchPos);

  if (found)
    XmTextSetTopCharacter(text, searchPos);

  while (found)
    {
    XmTextSetHighlight(text, searchPos, searchPos+len, XmHIGHLIGHT_SELECTED);
    currPos = searchPos + 1;
    found = XmTextFindString(text, currPos, target, XmTEXT_FORWARD, &searchPos);
    }

  XtFree(target);

}	/* END SEARCH */

/* -------------------------------------------------------------------- */
TextWindow::~TextWindow()
{
  Clear();

}

/* END TEXTWINDOW.CC */
