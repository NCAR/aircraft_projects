/*
-------------------------------------------------------------------------
OBJECT NAME:	XFonts.h

FULL NAME:	Load X fonts

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef XFONTS_H
#define XFONTS_H

#include <X11/Intrinsic.h>
#include <X11/StringDefs.h>

#include <string>
#include <iostream>

#define	MAX_FONTS	6

/* -------------------------------------------------------------------- */
class XFonts {

public:
	XFonts(Widget shell);

  enum	size { Point24, Point18, Point14, Point12, Point10 };

  const XFontStruct	*Font(int idx) const { return(fontInfo[idx]); }

  int	StringWidth(int idx, const std::string& s) const
	{ return(XTextWidth(fontInfo[idx], s.c_str(), s.length())); }

  int	StringWidth(const XFontStruct *font, const std::string& s) const
	{ return(XTextWidth((XFontStruct *)font, s.c_str(), s.length())); }

private:
  XFontStruct   *fontInfo[MAX_FONTS];

};	/* END XFONTS.H */

#endif
