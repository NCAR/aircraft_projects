/*
-------------------------------------------------------------------------
OBJECT NAME:	validate.cc

FULL NAME:	Misc. Validate Functions

ENTRY POINTS:	ValidateTime()
		ValidateFloat()
		ValidateInteger()

STATIC FNS:	none

DESCRIPTION:	

REFERENCES:	none

REFERENCED BY:	Misc Widgets.

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include <cstdio>
#include <cstdlib>

#include <Xm/TextF.h>

/* -------------------------------------------------------------------- */
void ValidateTime(Widget w, XtPointer client, XtPointer call)
{
  unsigned	hour, min, sec;
  char		*p = XmTextFieldGetString(w), buffer[128];

  if (strlen(p) == 0)
    return;

  hour = min = sec = 0;

  if (strchr(p, ':') != (char *)0)
    sscanf(p, "%u:%u:%u", &hour, &min, &sec);
  else
    sscanf(p, "%02u%02u%02u", &hour, &min, &sec);

  if (hour > 48) hour = 48;
  if (min > 59) min = 59;
  if (sec > 59) sec = 59;

  sprintf(buffer, "%02d:%02d:%02d", hour, min, sec);
  XmTextFieldSetString(w, buffer);
  XtFree(p);

}	/* END VALIDATETIME */

/* -------------------------------------------------------------------- */
void ValidateInteger(Widget w, XtPointer client, XtPointer call)
{
  char	*p, buffer[128];

  p = XmTextFieldGetString(w);

  sprintf(buffer, "%d", atoi(p));
  XmTextFieldSetString(w, buffer);

  XtFree(p);

}	/* END VALIDATEINTEGER */

/* -------------------------------------------------------------------- */
void ValidateFloat(Widget w, XtPointer client, XtPointer call)
{
  char	*p, buffer[128];

  p = XmTextFieldGetString(w);

  sprintf(buffer, (char *)client, atof(p));
  XmTextFieldSetString(w, buffer);

  XtFree(p);

}	/* END VALIDATEFLOAT */

/* END VALIDATE.CC */
