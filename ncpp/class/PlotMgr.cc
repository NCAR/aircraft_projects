/*
-------------------------------------------------------------------------
OBJECT NAME:	PlotMgr.cc

FULL NAME:	Interface class

ENTRY POINTS:	PlotManager()

STATIC FNS:	

DESCRIPTION:	

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-9
-------------------------------------------------------------------------
*/

#include "PlotMgr.h"

#include <Xm/Frame.h>
#include <Xm/Label.h>
#include <Xm/RowColumn.h>
#include <Xm/ToggleB.h>

static struct	// Initialization parameters for EditWindow.
        {
        PlotType        plotType;
        char            name[20];
        bool            zAxis;
        }
      args[] = {
        { XY, "editXY", false },
        { XYZ, "editXYZ", true }
        };


static char *nNormalize[] =
        { "None", "Linear", "Log", NULL };

static char *nPanel[] =
        { "1x1", "2x3", "3x4", "4x6", "5x7", "6x8", "7x9", NULL };


/* -------------------------------------------------------------------- */
PlotManager::PlotManager(const Widget parent, const Widget drawA) :
	WinForm(parent, "control", RowColumn),
	fonts(parent), colors(drawA), blackPen(drawA), colorPen(drawA)
{
  Arg		args[4];
  Cardinal	n;
  Widget	frame[8], title[8], RC[8], plRC[2], grid, bandw, ditc;

  extern Canvas		*mainCanvas;
  extern SetManager	setMgr, movieSetMgr;

  n = 0;
  frame[0] = XmCreateFrame(Window(), "plotFrame", args, n);
  frame[1] = XmCreateFrame(Window(), "probeFrame", args, n);
  XtManageChild(frame[0]); XtManageChild(frame[1]);

  n = 0;
  title[0] = XmCreateLabel(frame[0], "Data Source", args, n);
  title[1] = XmCreateLabel(frame[1], "Plot Type", args, n);
  XtManageChild(title[0]); XtManageChild(title[1]);

  n = 0;
  RC[0] = XmCreateRowColumn(frame[0], "probeSelRC", args, n);
  RC[5] = XmCreateRowColumn(frame[1], "plotRC", args, n);
  XtManageChild(RC[0]); XtManageChild(RC[5]);


  n = 0;
  frame[0] = XmCreateFrame(RC[0], "fileFrame", args, n);
  frame[1] = XmCreateFrame(RC[0], "probeFrame", args, n);
  frame[2] = XmCreateFrame(RC[0], "dataFrame", args, n);
  frame[3] = XmCreateFrame(RC[0], "computeFrame", args, n);
  XtManageChildren(frame, 4);

  n = 0;
  title[0] = XmCreateLabel(frame[0], "Current File", args, n);
  title[1] = XmCreateLabel(frame[1], "Probes", args, n);
  title[2] = XmCreateLabel(frame[2], "Data Type", args, n);
  title[3] = XmCreateLabel(frame[3], "Concentrations", args, n);
  XtManageChild(title[0]); XtManageChild(title[1]);
  XtManageChild(title[2]); XtManageChild(title[3]);

  n = 0;
  RC[1] = XmCreateRadioBox(frame[0], "fileRC", args, n);
  RC[2] = XmCreateRowColumn(frame[1], "probeRC", args, n);
  RC[3] = XmCreateRowColumn(frame[2], "dataRC", args, n);
  RC[4] = XmCreateRadioBox(frame[3], "plRC", args, n);
  XtManageChild(RC[1]); XtManageChild(RC[2]);
  XtManageChild(RC[3]); XtManageChild(RC[4]);


  /* Plot Type Toggle Buttons.
   */
  n = 0;
  plRC[0] = XmCreateRadioBox(RC[5], "plotRB", args, n);
  plRC[1] = XmCreateRowColumn(RC[5], "panel", args, n);
  XtManageChildren(plRC, 2);
/*
  n = 0;
  plotTypeB[0] = XmCreateToggleButton(plRC[0], "XY", NULL, n);
  plotTypeB[1] = XmCreateToggleButton(plRC[0], "XYZ", NULL, n);
  XtManageChildren(plotTypeB, N_PLOTTYPES);

  XtAddCallback(plotTypeB[0], XmNvalueChangedCallback,
		(XtCallbackProc)SetPlotTypeCB, (XtPointer)XY);
  XtAddCallback(plotTypeB[1], XmNvalueChangedCallback,
		(XtCallbackProc)SetPlotTypeCB, (XtPointer)XYZ);
 
  XmToggleButtonSetState(plotTypeB[0], True, False);
  plotType = XY;

XtSetSensitive(plotTypeB[0], false);
XtSetSensitive(plotTypeB[1], false);
*/

  /* nRows x nCols
   */
  int           i;
  Widget        slPD, slOpMenu, slButts[10];
  XmString      name;


  n = 0;
  slPD = XmCreatePulldownMenu(plRC[1], "nPanPullDown", args, n);

  n = 0;
  XtSetArg(args[n], XmNsubMenuId, slPD); ++n;
  slOpMenu = XmCreateOptionMenu(plRC[1], "nPanMenu", args, n);
  XtManageChild(slOpMenu);


  for (i = 0; nPanel[i]; ++i)
    {
    name = XmStringCreateLocalized(nPanel[i]);

    n = 0;
    XtSetArg(args[n], XmNlabelString, name); ++n;
    slButts[i] = XmCreatePushButton(slPD, "opMenB", args, n);
    XtAddCallback(slButts[i], XmNactivateCallback, Set_nPanels,
                (XtPointer)nPanel[i]);

    XmStringFree(name);
    }

  XtManageChildren(slButts, i);



  /* Normalization
   */
  Widget        nlPD, nlOpMenu, nlButts[3];


  n = 0;
  nlPD = XmCreatePulldownMenu(plRC[1], "normPanPullDown", args, n);

  n = 0;
  XtSetArg(args[n], XmNsubMenuId, nlPD); ++n;
  nlOpMenu = XmCreateOptionMenu(plRC[1], "normPanMenu", args, n);
  XtManageChild(nlOpMenu);

  name = XmStringCreateLocalized("None");
  name = XmStringCreateLocalized("Linear");
  name = XmStringCreateLocalized("Log");

  for (i = 0; nNormalize[i]; ++i)
    {
    name = XmStringCreateLocalized(nNormalize[i]);

    n = 0;
    XtSetArg(args[n], XmNlabelString, name); ++n;
    nlButts[i] = XmCreatePushButton(nlPD, "opMenB", args, n);
    XtAddCallback(nlButts[i], XmNactivateCallback, SetNormalization,
                (XtPointer)nNormalize[i]);

    XmStringFree(name);
    }

  XtManageChildren(nlButts, i);



  n = 0;
  bandw = XmCreateToggleButton(plRC[1], "Black & White", args, n);
  XtManageChild(bandw);
  XtAddCallback(bandw, XmNvalueChangedCallback, ToggleColor_CB, NULL);

  n = 0;
  grid = XmCreateToggleButton(plRC[1], "Grid", args, n);
  XtManageChild(grid);
  XtAddCallback(grid, XmNvalueChangedCallback, ToggleGrid_CB, NULL);

  n = 0;
  ditc = XmCreateToggleButton(plRC[1], "Data in the corner", args, n);
  XtManageChild(ditc);
  XtAddCallback(ditc, XmNvalueChangedCallback, ToggleDITC_CB, NULL);

  CreateDataSourceWidgets(RC[1], RC[2], RC[3], RC[4]);



  /* Create Fonts, colors, and then PlotTypes.
   */
  plot[0] = new PlotInfo(XY, setMgr,
			*mainCanvas, fonts, colors, blackPen, colorPen);
  plot[1] = new PlotInfo(XYZ, setMgr,
			*mainCanvas, fonts, colors, blackPen, colorPen);
 
  editParms[0] = editParms[1] = NULL;

  SetFileNames();

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void PlotManager::SetDataTypes(DataType dt)
{
  for (int i = 0; i < N_PLOTTYPES; ++i)
    plot[i]->SetDataTypes(dt);

  if (editParms[plotType])
    editParms[plotType]->SetActiveNumberPanels(plot[plotType]->nPanels);

}	/* END SETDATATYPES */

/* -------------------------------------------------------------------- */
void PlotManager::EditParms(Widget parent, int idx)
{
  if (!editParms[idx])
    editParms[idx] = new EditPlotParms(parent,
        args[idx].plotType, args[idx].name, MAX_PANELS, args[idx].zAxis);

  SetParms(idx);
  editParms[idx]->SetActiveNumberPanels(plot[idx]->nPanels);
  editParms[idx]->PopUp();

}	/* END EDITPARMS */

/* -------------------------------------------------------------------- */
void PlotManager::GenerateAutoTitles(DataFile& file)
{
  std::string	title;
  std::string	subTitle;

  title = file.ProjectName();

  if (file.FlightNumber().length() > 0)
    {
    if (file.ProjectName().length() > 0)
      title += ", ";
 
    title += "Flight #";
    title += file.FlightNumber();
    }
 
  subTitle = file.FlightDate();


  for (int i = 0; i < N_PLOTTYPES; ++i)
    {
    plot[i]->SetTitle(title);
    plot[i]->SetSubtitle(subTitle);
    }

}	/* END GENERATEAUTOTITLES */

/* -------------------------------------------------------------------- */
void PlotManager::ToggleDITC()
{
  for (int i = 0; i < N_PLOTTYPES; ++i)
    plot[i]->ToggleDITC();

}	/* END TOGGLEDITC */

/* -------------------------------------------------------------------- */
void PlotManager::ToggleGrid()
{
  for (int i = 0; i < N_PLOTTYPES; ++i)
    plot[i]->ToggleGrid();

}	/* END TOGGLEGRID */

/* -------------------------------------------------------------------- */
void PlotManager::ToggleColor()
{
  for (int i = 0; i < N_PLOTTYPES; ++i)
    plot[i]->ToggleColor();

}	/* END TOGGLECOLOR */

/* -------------------------------------------------------------------- */
void PlotManager::ToggleAutoTitle(int idx)
{
  PlotInfo	*pi = plot[idx];
  EditPlotParms	*ew = editParms[idx];

  XtSetSensitive(ew->title, pi->autoTitles);
  XtSetSensitive(ew->subTitle, pi->autoTitles);

  pi->autoTitles = 1 - pi->autoTitles;

}	/* END TOGGLEAUTOTITLE */

/* -------------------------------------------------------------------- */
void PlotManager::ToggleAutoLabel(int idx)
{
  PlotInfo	*pi = plot[idx];
  EditPlotParms	*ew = editParms[idx];
  Panel		*p = pi->panel[ew->CurrentPanel()];

  XtSetSensitive(ew->xAxis.label, p->AutoLabels);
  XtSetSensitive(ew->yAxis[0].label, p->AutoLabels);

  if (ew->yRight())
    XtSetSensitive(ew->yAxis[1].label, p->AutoLabels);

  if (ew->isZaxis())
    XtSetSensitive(ew->zAxis.label, p->AutoLabels);

  p->AutoLabels = 1 - p->AutoLabels;

}	/* END AUTOLABEL */

/* -------------------------------------------------------------------- */
void PlotManager::ToggleAutoScale(int idx)
{
  PlotInfo	*pi = plot[idx];
  EditPlotParms	*ew = editParms[idx];
  Panel		*p = pi->panel[ew->CurrentPanel()];

  XtSetSensitive(ew->xAxis.min, p->AutoScale);
  XtSetSensitive(ew->xAxis.max, p->AutoScale);
  XtSetSensitive(ew->yAxis[0].min, p->AutoScale);
  XtSetSensitive(ew->yAxis[0].max, p->AutoScale);

  if (ew->yRight())
    {
    XtSetSensitive(ew->yAxis[1].min, p->AutoScale);
    XtSetSensitive(ew->yAxis[1].max, p->AutoScale);
    }

  if (ew->isZaxis())
    {
    XtSetSensitive(ew->zAxis.min, p->AutoScale);
    XtSetSensitive(ew->zAxis.max, p->AutoScale);
    }

  p->AutoScale = 1 - p->AutoScale;

}       /* END AUTOSCALE */

/* -------------------------------------------------------------------- */
void PlotManager::ToggleAutoTics(int idx)
{
  PlotInfo	*pi = plot[idx];
  EditPlotParms	*ew = editParms[idx];
  Panel		*p = pi->panel[ew->CurrentPanel()];

  XtSetSensitive(ew->xAxis.nMajorTics, p->AutoTics);
  XtSetSensitive(ew->xAxis.nMinorTics, p->AutoTics);
  XtSetSensitive(ew->yAxis[0].nMajorTics, p->AutoTics);
  XtSetSensitive(ew->yAxis[0].nMinorTics, p->AutoTics);

  if (ew->yRight())
    {
    XtSetSensitive(ew->yAxis[1].nMajorTics, p->AutoTics);
    XtSetSensitive(ew->yAxis[1].nMinorTics, p->AutoTics);
    }

  if (ew->isZaxis())
    {
    XtSetSensitive(ew->zAxis.nMajorTics, p->AutoTics);
    XtSetSensitive(ew->zAxis.nMinorTics, p->AutoTics);
    }

  p->AutoTics = 1 - p->AutoTics;

}       /* END AUTOTICS */

/* -------------------------------------------------------------------- */
void PlotManager::ApplyParms(int idx, DataFile& currentFile)
{
  int		i, n;
  PlotInfo	*pi = plot[idx];
  EditPlotParms	*ew = editParms[idx];
  Panel		*p = pi->panel[ew->CurrentPanel()];

  if (ew == NULL)
    return;

  pi->autoTitles = XmToggleButtonGetState(ew->autoTitles);
  p->AutoLabels = XmToggleButtonGetState(ew->autoLabels);
  p->AutoScale = XmToggleButtonGetState(ew->autoScale);
  p->AutoTics = XmToggleButtonGetState(ew->autoTics);

  GetTextString(ew->title, pi->title);
  GetTextString(ew->subTitle, pi->subTitle);

  GetTextString(ew->xAxis.label, p->xAxis.label);
  p->xAxis.logScale = XmToggleButtonGetState(ew->xAxis.logScale);
  p->xAxis.invertAxis = XmToggleButtonGetState(ew->xAxis.invertAxis);
  p->xAxis.min = GetTextFloat(ew->xAxis.min);
  p->xAxis.max = GetTextFloat(ew->xAxis.max);
  p->xAxis.nMajorTics = GetTextInt(ew->xAxis.nMajorTics);
  p->xAxis.nMinorTics = GetTextInt(ew->xAxis.nMinorTics);

  n = ew->yRight() ? 2 : 1;

  for (i = 0; i < n; ++i)
    {
    GetTextString(ew->yAxis[i].label, p->yAxis.label);
    p->yAxis.logScale = XmToggleButtonGetState(ew->yAxis[i].logScale);
    p->yAxis.invertAxis = XmToggleButtonGetState(ew->yAxis[i].invertAxis);
    p->yAxis.min = GetTextFloat(ew->yAxis[i].min);
    p->yAxis.max = GetTextFloat(ew->yAxis[i].max);
    p->yAxis.nMajorTics = GetTextInt(ew->yAxis[i].nMajorTics);
    p->yAxis.nMinorTics = GetTextInt(ew->yAxis[i].nMinorTics);
    }

  if (ew->isZaxis())
    {
    GetTextString(ew->zAxis.label, p->zAxis.label);
    p->zAxis.logScale = XmToggleButtonGetState(ew->zAxis.logScale);
    p->zAxis.invertAxis = XmToggleButtonGetState(ew->zAxis.invertAxis);
    p->zAxis.min = GetTextFloat(ew->zAxis.min);
    p->zAxis.max = GetTextFloat(ew->zAxis.max);
    p->zAxis.nMajorTics = GetTextInt(ew->zAxis.nMajorTics);
    p->zAxis.nMinorTics = GetTextInt(ew->zAxis.nMinorTics);
    }

  GenerateAutoTitles(currentFile);
  pi->SetDefaultLabels(ew->CurrentPanel());
  pi->AutoScale(ew->CurrentPanel());
  pi->SetDefaultTics(ew->CurrentPanel());

  SetParms(idx);
  DrawImage();

}	/* END APPLYPARMS */

/* -------------------------------------------------------------------- */
void PlotManager::SetParms(int idx)
{
  int		i, n;
  char		genSpace[32];
  PlotInfo	*pi = plot[idx];
  EditPlotParms	*ew = editParms[idx];
  Panel		*p = pi->panel[ew->CurrentPanel()];

  if (ew == NULL)
    return;

  XmToggleButtonSetState(ew->autoTitles, pi->autoTitles, false);
  XmToggleButtonSetState(ew->autoLabels, p->AutoLabels, false);
  XmToggleButtonSetState(ew->autoScale, p->AutoScale, false);
  XmToggleButtonSetState(ew->autoTics, p->AutoTics, false);

  XmTextFieldSetString(ew->title, (char *)pi->title.c_str());
  XmTextFieldSetString(ew->subTitle, (char *)pi->subTitle.c_str());

  XmTextFieldSetString(ew->xAxis.label, (char *)p->xAxis.label.c_str());

  XmToggleButtonSetState(ew->xAxis.logScale, p->xAxis.logScale, false);
  XmToggleButtonSetState(ew->xAxis.invertAxis, p->xAxis.invertAxis, false);

  sprintf(genSpace, "%d", p->xAxis.nMajorTics);
  XmTextFieldSetString(ew->xAxis.nMajorTics, genSpace);

  sprintf(genSpace, "%d", p->xAxis.nMinorTics);
  XmTextFieldSetString(ew->xAxis.nMinorTics, genSpace);

  sprintf(genSpace, "%e", p->xAxis.min);
  XmTextFieldSetString(ew->xAxis.min, genSpace);

  sprintf(genSpace, "%e", p->xAxis.max);
  XmTextFieldSetString(ew->xAxis.max, genSpace);

  XtSetSensitive(ew->xAxis.label, !p->AutoLabels);
  XtSetSensitive(ew->xAxis.nMajorTics, !p->AutoTics);
  XtSetSensitive(ew->xAxis.nMinorTics, !p->AutoTics);
  XtSetSensitive(ew->xAxis.min, !p->AutoScale);
  XtSetSensitive(ew->xAxis.max, !p->AutoScale);

  n = ew->yRight() ? 2 : 1;

  for (i = 0; i < n; ++i)
    {
    XmTextFieldSetString(ew->yAxis[i].label, (char *)p->yAxis.label.c_str());
    XmToggleButtonSetState(ew->yAxis[i].logScale, p->yAxis.logScale, false);
    XmToggleButtonSetState(ew->yAxis[i].invertAxis, p->yAxis.invertAxis, false);

    sprintf(genSpace, "%d", p->yAxis.nMajorTics);
    XmTextFieldSetString(ew->yAxis[i].nMajorTics, genSpace);

    sprintf(genSpace, "%d", p->yAxis.nMinorTics);
    XmTextFieldSetString(ew->yAxis[i].nMinorTics, genSpace);

    sprintf(genSpace, "%e", p->yAxis.min);
    XmTextFieldSetString(ew->yAxis[i].min, genSpace);

    sprintf(genSpace, "%e", p->yAxis.max);
    XmTextFieldSetString(ew->yAxis[i].max, genSpace);

    XtSetSensitive(ew->yAxis[i].label, !p->AutoLabels);
    XtSetSensitive(ew->yAxis[i].nMajorTics, !p->AutoTics);
    XtSetSensitive(ew->yAxis[i].nMinorTics, !p->AutoTics);
    XtSetSensitive(ew->yAxis[i].min, !p->AutoScale);
    XtSetSensitive(ew->yAxis[i].max, !p->AutoScale);
    }


  if (ew->isZaxis())
    {
    XmTextFieldSetString(ew->zAxis.label, (char *)p->zAxis.label.c_str());
    XmToggleButtonSetState(ew->zAxis.logScale, p->zAxis.logScale, false);
    XmToggleButtonSetState(ew->zAxis.invertAxis, p->zAxis.invertAxis, false);

    sprintf(genSpace, "%d", p->zAxis.nMajorTics);
    XmTextFieldSetString(ew->zAxis.nMajorTics, genSpace);

    sprintf(genSpace, "%d", p->zAxis.nMinorTics);
    XmTextFieldSetString(ew->zAxis.nMinorTics, genSpace);

    sprintf(genSpace, "%e", p->zAxis.min);
    XmTextFieldSetString(ew->zAxis.min, genSpace);

    sprintf(genSpace, "%e", p->zAxis.max);
    XmTextFieldSetString(ew->zAxis.max, genSpace);

    XtSetSensitive(ew->zAxis.label, !p->AutoLabels);
    XtSetSensitive(ew->zAxis.nMajorTics, !p->AutoTics);
    XtSetSensitive(ew->zAxis.nMinorTics, !p->AutoTics);
    XtSetSensitive(ew->zAxis.min, !p->AutoScale);
    XtSetSensitive(ew->zAxis.max, !p->AutoScale);
    }

  XtSetSensitive(ew->title, !pi->autoTitles);
  XtSetSensitive(ew->subTitle, !pi->autoTitles);

}	/* END SETPARMS */

/* END PLOTMGR.CC */
