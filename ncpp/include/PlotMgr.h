/*
-------------------------------------------------------------------------
OBJECT NAME:	PlotMgr.h

FULL NAME:	Plot Manager

TYPE:		Interface class

DESCRIPTION:	Intermediator between PlotInfo & GUI (EditParms & Control)
		and PlotX

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-9
-------------------------------------------------------------------------
*/

#ifndef PLOTMGR_H
#define PLOTMGR_H

#include "define.h"

#include "Canvas.h"
#include "DataFile.h"
#include "DataSource.h"
#include "EditPlotParms.h"
#include "PlotInfo.h"
#include "SetMgr.h"
#include "Window.h"
#include "Colors.h"
#include "XFonts.h"
#include "XPen.h"


/* -------------------------------------------------------------------- */
class PlotManager : public WinForm, public DataSource {

public:
	PlotManager(const Widget parent, const Widget drawA);

  friend void	SetPlotTypeCB(Widget, XtPointer, XtPointer);

  void	GenerateAutoTitles(DataFile& file);

  PlotType	CurrentPlotType() const	{ return(plotType); }

  void	Resize()			{ plot[plotType]->ResizeX(); }
  void	DrawImage()			{ plot[plotType]->Draw(); }
  void	Print(char *name)		{ plot[plotType]->Print(name); }

  std::string	Title()			{ return(plot[plotType]->Title()); }
  std::string	SubTitle()		{ return(plot[plotType]->SubTitle()); }

  void	EditParms(Widget shell, int idx);
  void	ApplyParms(int idx, DataFile& file);
  void	SetParms(int idx);
  void	SetPlotType(PlotType newPT)	{ plotType = newPT; }
  void	SetLineWidth(int newLW)	{ plot[plotType]->SetLineWidth(newLW); }
  void	ToggleDITC();
  void	ToggleGrid();
  void	ToggleColor();
  void	ToggleAutoTitle(int idx);
  void	ToggleAutoLabel(int idx);
  void	ToggleAutoScale(int idx);
  void	ToggleAutoTics(int idx);

  void	SetDataTypes(DataType dt);
  void  SetRowsCols(int rows, int cols)
			{ plot[plotType]->SetRowsCols(rows, cols); }

  void  SetNormalize(NormType normalize)
			{ plot[plotType]->SetNormalization(normalize); }

  void	SavePNG(const char fileName[], XImage *image)
			{ colors.SavePNG(fileName, image); }

private:
  Widget	plotTypeB[N_PLOTTYPES];
  PlotType	plotType;

  PlotInfo	*plot[N_PLOTTYPES];		// Postage, 3d.
  EditPlotParms	*editParms[N_PLOTTYPES];	// Postage, 3d.

  Colors	colors;
  XFonts	fonts;
  XPen		blackPen, colorPen;


};	/* END PLOTMGR.H */

#endif
