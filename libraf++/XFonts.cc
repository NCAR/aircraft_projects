/*
-------------------------------------------------------------------------
OBJECT NAME:	XFonts.cc

FULL NAME:	

ENTRY POINTS:	

STATIC FNS:	

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "XFonts.h"


/* Values for reading Font Resources    */
#define XtNfont24       "font24"
#define XtCFont24       "Font24"
#define XtNfont18       "font18"
#define XtCFont18       "Font18"
#define XtNfont14       "font14"
#define XtCFont14       "Font14"
#define XtNfont12       "font12"
#define XtCFont12       "Font12"
#define XtNfont10       "font10"
#define XtCFont10       "Font10"
 
typedef struct _insRec
        {
        char    *font24;
        char    *font18;
        char    *font14;
        char    *font12;
        char    *font10;
        } instanceRec;

static XtResource resources[] = {
	{XtNfont24, XtCFont24, XtRString, sizeof(char *),
	 XtOffsetOf(instanceRec, font24), XtRString, NULL},

	{XtNfont18, XtCFont18, XtRString, sizeof(char *),
	 XtOffsetOf(instanceRec, font18), XtRString, NULL},

	{XtNfont14, XtCFont14, XtRString, sizeof(char *),
	 XtOffsetOf(instanceRec, font14), XtRString, NULL},

	{XtNfont12, XtCFont12, XtRString, sizeof(char *),
	 XtOffsetOf(instanceRec, font12), XtRString, NULL},

	{XtNfont10, XtCFont10, XtRString, sizeof(char *),
	 XtOffsetOf(instanceRec, font10), XtRString, NULL},
	};

/* -------------------------------------------------------------------- */
XFonts::XFonts(Widget shell)
{
  instanceRec	iv;
  Display	*dpy = XtDisplay(shell);

  XtGetApplicationResources(shell, (caddr_t)&iv, resources,
                            XtNumber(resources), NULL, 0);

  if ((fontInfo[Point24] = XLoadQueryFont(dpy, iv.font24)) == NULL ||
      (fontInfo[Point18] = XLoadQueryFont(dpy, iv.font18)) == NULL ||
      (fontInfo[Point14] = XLoadQueryFont(dpy, iv.font14)) == NULL ||
      (fontInfo[Point12] = XLoadQueryFont(dpy, iv.font12)) == NULL ||
      (fontInfo[Point10] = XLoadQueryFont(dpy, iv.font10)) == NULL)
    std::cerr << "XFonts: can't load font.\n";

}	/* END CONSTRUCTOR */

/* END XFONTS.CC */
