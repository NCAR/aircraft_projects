/*
-------------------------------------------------------------------------
OBJECT NAME:	gettext.cc

FULL NAME:	Retreive values from text widgets.

ENTRY POINTS:	GetTextFloat()
		GetTextInt()
		GetTextString()

STATIC FNS:	none

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1998
-------------------------------------------------------------------------
*/

#include <cstdlib>
#include <string>

#include <Xm/TextF.h>

using namespace std;

/* -------------------------------------------------------------------- */
int GetTextInt(const Widget w)
{
  char  *p;
  int   n;

  p = XmTextFieldGetString(w);
  n = atoi(p);
  XtFree(p);

  return(n);

}

/* -------------------------------------------------------------------- */
float GetTextFloat(const Widget w)
{
  char  *p;
  float x;

  p = XmTextFieldGetString(w);
  x = atof(p);
  XtFree(p);

  return(x);

}

/* -------------------------------------------------------------------- */
void GetTextString(const Widget w, string& s)
{
  char  *p;

  p = XmTextFieldGetString(w);
  s = p;
  XtFree(p);

}

/* END GETTEXT.CC */
