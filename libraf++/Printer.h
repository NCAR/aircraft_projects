/*
-------------------------------------------------------------------------
OBJECT NAME:	Printer.h

FULL NAME:	Printer Setup Class

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef PRINTER_H
#define PRINTER_H

#include "Window.h"

#include <Xm/Frame.h>
#include <Xm/Label.h>
#include <Xm/PushB.h>
#include <Xm/RowColumn.h>
#include <Xm/TextF.h>
#include <Xm/ToggleB.h>

#define TOTAL_PARMS	3
#define MAX_PRINTERS    20


/* -------------------------------------------------------------------- */
class Printer : public WinForm {

public:
  enum layout { LANDSCAPE, PORTRAIT };

	Printer(Widget parent);
  void	PopUp();
  void	ApplyParms();

  layout Shape()	{ return(shape); }
  char	*lpCommand()	{ return(lp_command); }
  bool	Color()		{ return(color); }
  int	LineWidth()	{ return(lineWidth); }
  int	Width()		{ return((int)(dpi * width)); }
  int	Height()	{ return((int)(dpi * height)); }

  float	WidthRatio()	{ return(width / (shape == LANDSCAPE ? 11.0 : 8.5)); }
  float	HeightRatio()	{ return(height / (shape == LANDSCAPE ? 8.5 : 11.0)); }
  float	FontRatio();

  void	SetShape(layout newShape);
  void	SetPrinter(char newPrinter[]);
  void	SetColor(bool c)	{ color = c; }
  void	SetCommand(char s[])	{ strcpy(lp_command, s); }
  void	SetLineWidth(int w)	{ if (w > 0 && w < 10) lineWidth = w; }

private:
  static const int     dpi = 288;

  Widget	parmsText[TOTAL_PARMS], shapeB[2], colorB[2];

  char		lp_command[64], *printer_list[MAX_PRINTERS];
  float		width, height;
  layout	shape;
  bool		color;
  int		lineWidth;

  void		setParms(), GetPrinterList();

};	/* END PRINTER.H */

#endif
