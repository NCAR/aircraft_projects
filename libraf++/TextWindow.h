/*
-------------------------------------------------------------------------
OBJECT NAME:	TextWindow.h

FULL NAME:	Create Basic scrolled text window.

TYPE:		Base class

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1998
-------------------------------------------------------------------------
*/

#ifndef TEXTWIN_H
#define TEXTWIN_H


#include <Xm/Text.h>
#include "Window.h"

void    PrintText(Widget, XtPointer, XtPointer),
        DismissText(Widget, XtPointer, XtPointer),
        SaveText(Widget, XtPointer, XtPointer),
        SearchText(Widget, XtPointer, XtPointer);


/* -------------------------------------------------------------------- */
class TextWindow : public WinForm {

public:
	TextWindow(const Widget parent, char name[]);
	~TextWindow();

  void	Clear()	{ XmTextSetString(text, ""); }
  void	Append(const char txt[])
	{ XmTextInsert(text, XmTextGetLastPosition(text), (char *)txt); }

  void	Search();

  void MoveTo(int pos)	{ XmTextSetTopCharacter(text, pos); }

private:
  Widget	text, searchTxt;

};	/* END TEXTWINDOW.H */

#endif
