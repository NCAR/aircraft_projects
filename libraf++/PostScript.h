/*
-------------------------------------------------------------------------
OBJECT NAME:    PostScript.h
 
FULL NAME:      Printing/PostScript header include file.
 
TYPE:		

DESCRIPTION:	Postscript version of class PlotX

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef POSTSCRIPT_H
#define POSTSCRIPT_H

#include <cstdlib>
#include <cstdio>
#include <string>

#include "Printer.h"


/* -------------------------------------------------------------------- */
class PostScript {

public:
	PostScript(char *outFile, char progName[], const std::string& title, float scale);
	~PostScript();

  void	MoveTo(int x, int y)	{ fprintf(fp,"%d %d m\n", x, y); }
  void	LineTo(int x, int y)	{ fprintf(fp,"%d %d l\n", x, y); }
  void	rMoveTo(int x, int y)	{ fprintf(fp,"%d %d rm\n", x, y); }
  void	rLineTo(int x, int y)	{ fprintf(fp,"%d %d rl\n", x, y); }
  void	ShowStr(char str[])	{ fprintf(fp,"(%s) s\n", str); }
  void	ShowStr(std::string str)	{ fprintf(fp,"(%s) s\n", str.c_str()); }
  void	SetLineWidth(int width)	{ fprintf(fp,"%d setlinewidth\n", width); }

  void	Rotate(int degrees)	{ fprintf(fp,"%d rotate\n", degrees); }
  void	MoveOrigin(int x, int y){ fprintf(fp,"%d %d translate\n", x, y); }
  void	Stroke()		{ fprintf(fp,"stroke\n"); }
  void	SetColor(float *rgb)
	{ fprintf(fp, "stroke %g %g %g setrgbcolor\n", rgb[0],rgb[1],rgb[2]); }
  void	SetFont(int size);

  void	DrawBox(int th, int lv, int bh, int rv);

  void	SetClipping(int vd, int hd);
  void	ClearClipping();

  void	SetDash(int idx)	{ fprintf(fp,"stroke [%d] 0 setdash\n", (idx+1)<<3); }
  void	ClearDash()		{ fprintf(fp,"[] 0 setdash\n"); }

  // Issue generic command.
  void	Issue(char str[])	{ fprintf(fp,str); }

private:
  FILE	*fp;
  bool	file;

  void	PSheader(char progName[], const std::string& title, float scale);

};	/* END POSTSCRIPT.H */

#endif
