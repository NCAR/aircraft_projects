/*
-------------------------------------------------------------------------
OBJECT NAME:	EditWindow.h

FULL NAME:	Create Basic Edit Parameters window.

TYPE:		Base class

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1998
-------------------------------------------------------------------------
*/

#ifndef EDITWIN_H
#define EDITWIN_H
#include "define.h"

#include <Xm/Frame.h>
#include <Xm/Label.h>
#include <Xm/TextF.h>
#include <Xm/ToggleB.h>
#include "Window.h"

struct ep_axisInfo  // This needs to match axisInfo in Panel.h
	{
	Widget	label, logScale, invertAxis, nMajorTics, nMinorTics,
		min, max;
	};

/* -------------------------------------------------------------------- */
class EditWindow : public WinForm {

public:
	EditWindow(const Widget parent, PlotType plotType, char name[], int nPanels, bool zAxis);

  friend class PlotManager;

  int	CurrentPanel();

  void	SetActiveNumberPanels(int n);

  bool	AutoTitles() { return(XmToggleButtonGetState(autoTitles)); }
  bool	AutoLabels();
  bool	AutoScale();
  bool	AutoTics();

  bool	isZaxis()	{ return(zaxis); }
  bool	yRight()	{ return(yright); }


private:
  int	nPanels, currentPanel;

  bool	zaxis, yright;

  Widget createTitles(Widget parent);
  Widget createLabels(Widget parent);
  Widget createMinMax(Widget parent);
  Widget createLogLin(Widget parent);
  Widget createNtics(Widget parent);
  Widget createInvert(Widget parent);

  Widget createLineItem(Widget parent, char lbl[], char txt[]);
  Widget addToLineItem(char lbl[], char txt[]);
  void   addPanelButtons(Widget parent);

  Widget RC[12], panelB[MAX_PANELS], tmpRC;

  Widget title, subTitle;
  Widget autoTitles, autoLabels, autoScale, autoTics;

  ep_axisInfo	xAxis, yAxis[2], zAxis;

};	/* END EDITWINDOW.H */

#endif
