/*
-------------------------------------------------------------------------
OBJECT NAME:	PlotInfo.cc

FULL NAME:	Plot Information/Parameters

ENTRY POINTS:	PlotInfo()
		PopUp()

STATIC FNS:	

DESCRIPTION:	

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-2001
-------------------------------------------------------------------------
*/

#include "PlotInfo.h"

extern Printer	*printerSetup;

/* -------------------------------------------------------------------- */
PlotInfo::PlotInfo(PlotType pt, SetManager& sm, Canvas& da, XFonts& f, Colors& c, XPen& bp, XPen& cp) : plotType(pt), sets(sm), canvas(da), fonts(f), colors(c), blackPen(bp), colorPen(cp)
{
  grid = false;
  color = true;
  autoTitles = true;
  plotParmsChanged = true;

  nCols = nRows = 0;
  nPanels = 0;
  lineWidth = 1;
  dataTypes = (DataType)0;
  nCols = nRows = 1;
  normalization = NONE;

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void PlotInfo::SetTitle(const std::string& newTitle)
{
  if (autoTitles)
    title = newTitle;

}	/* END SETTITLE */

/* -------------------------------------------------------------------- */
void PlotInfo::SetSubtitle(const std::string& newTitle)
{
  if (autoTitles)
    subTitle = newTitle;

}	/* END SETSUBTITLE */

/* -------------------------------------------------------------------- */
void PlotInfo::SetRowsCols(int rows, int cols)
{
  nRows = rows;
  nCols = cols;
  ResizeX();

}	/* SETROWSCOLS */

/* -------------------------------------------------------------------- */
void PlotInfo::UpdateSubtitle(DataSet *set)
{
  if (!autoTitles)
    return;

  int	idx = subTitle.find(",");

  if (!set)
    {
    if (idx != subTitle.npos)
      subTitle.replace(subTitle.find(","), subTitle.length(), "");
    return;
    }

  std::string temp(", ");
  temp += set->StartTime().c_str();
  temp += " - ";
  temp += set->EndTime().c_str();

  char tmp[20];

  sprintf(tmp, ", %d second average", sets.AveragingRate());
  temp += tmp;

  if (idx == subTitle.npos)
    subTitle.append(temp);
  else
    subTitle.replace(idx, subTitle.length(), temp);
 
}       /* END SETCURRENTSUBTITLE */

/* -------------------------------------------------------------------- */
void PlotInfo::SetDataTypes(DataType dt)
{
  int		idx = 0;
  DataType	oldTypes = dataTypes;

  dataTypes = dt;

  if (dataTypes & COUNTS && !(oldTypes & COUNTS))	// Add
    {
    insertPanel(idx);
    SetDefaultLabels(idx);
    }
  else
  if (!(dataTypes & COUNTS) && oldTypes & COUNTS)	// Delete
    {
    deletePanel(idx);
    }

  if (dataTypes & COUNTS)
    ++idx;


  if (dataTypes & CONCENTRATION && !(oldTypes & CONCENTRATION))	// Add
    {
    insertPanel(idx);
    SetDefaultLabels(idx);
    }
  else
  if (!(dataTypes & CONCENTRATION) && oldTypes & CONCENTRATION)	// Delete
    {
    deletePanel(idx);
    }

  if (dataTypes & CONCENTRATION)
    ++idx;


  if (dataTypes & SURFACE && !(oldTypes & SURFACE))	// Add
    {
    insertPanel(idx);
    SetDefaultLabels(idx);
    }
  else
  if (!(dataTypes & SURFACE) && oldTypes & SURFACE)	// Delete
    {
    deletePanel(idx);
    }

  if (dataTypes & SURFACE)
    ++idx;


  if (dataTypes & VOLUME && !(oldTypes & VOLUME))	// Add
    {
    insertPanel(idx);
    SetDefaultLabels(idx);
    }
  else
  if (!(dataTypes & VOLUME) && oldTypes & VOLUME)	// Delete
    {
    deletePanel(idx);
    }

  ResizeX();

}	/* END SETDATATYPES */

/* -------------------------------------------------------------------- */
void PlotInfo::SetNormalization(NormType n)
{
  normalization = n;

  for (int i = 0; i < nPanels; ++i)
    SetDefaultLabels(i);

}	/* END SETNORMALIZATION */

/* -------------------------------------------------------------------- */
void PlotInfo::SetDefaultLabels(int idx)
{
  if (!panel[idx]->AutoLabels)
    return;

  int	cnt = 0;

  if (dataTypes & COUNTS)
    {
    if (cnt++ == idx)
      {
      panel[idx]->xAxis.label = "Bin #";
      panel[idx]->yAxis.label = "Counts";
      panel[idx]->zAxis.label = "Time";
      return;
      }
    }

  if (dataTypes & CONCENTRATION)
    {
    if (cnt++ == idx)
      {
      panel[idx]->xAxis.label = "Diameter (um)";
      panel[idx]->yAxis.label = "N/cm3";
      panel[idx]->zAxis.label = "Time";
      }
    }

  if (dataTypes & SURFACE)
    {
    if (cnt++ == idx)
      {
      panel[idx]->xAxis.label = "Diameter (um)";
      panel[idx]->yAxis.label = "um2/cm3";
      panel[idx]->zAxis.label = "Time";
      }
    }

  if (dataTypes & VOLUME)
    {
    if (cnt++ == idx)
      {
      panel[idx]->xAxis.label = "Diameter (um)";
      panel[idx]->yAxis.label = "um3/cm3";
      panel[idx]->zAxis.label = "Time";
      }
    }

  if (normalization == LINEAR)
    panel[idx]->yAxis.label += "/um";

  if (normalization == LOG)
    panel[idx]->yAxis.label += "/log10(um)";


  // Convert the letter 'u' to the ASCII micron character
  for (int i = 0; i < panel[idx]->xAxis.label.length(); ++i)
    if (panel[idx]->xAxis.label[i] == 'u')
      panel[idx]->xAxis.label[i] = 0xb5;

  for (int i = 0; i < panel[idx]->yAxis.label.length(); ++i)
    if (panel[idx]->yAxis.label[i] == 'u')
      panel[idx]->yAxis.label[i] = 0xb5;

}	/* END SETDEFAULTLABELS */

/* -------------------------------------------------------------------- */
void PlotInfo::SetDefaultTics(int idx)
{
  Panel	*p = panel[idx];

  if (!p->AutoTics)
    return;

  if (p->xAxis.logScale)
    {
    p->xAxis.nMajorTics = (int)(log10(p->xAxis.max) - log10(p->xAxis.min)+0.5);
    p->xAxis.nMinorTics = 10;
    }
  else
    {
    p->xAxis.nMajorTics = 4;
    p->xAxis.nMinorTics = 2;
    }

  if (p->yAxis.logScale)
    {
    p->yAxis.nMajorTics = (int)(log10(p->yAxis.max) - log10(p->yAxis.min)+0.5);
    p->yAxis.nMinorTics = 10;
    }
  else
    {
    p->yAxis.nMajorTics = 5;
    p->yAxis.nMinorTics = 2;
    }

}	/* END SETDEFAULTTICS */

/* -------------------------------------------------------------------- */
void PlotInfo::AutoScale(int idx)
{
  Panel	*p = panel[idx];

  if (!p->AutoScale)
    return;

  int	cnt = 0;

  if (dataTypes & COUNTS)
    if (cnt++ == idx)
      AutoScaleAccum(sets, p);

  if (dataTypes & CONCENTRATION)
    if (cnt++ == idx)
      AutoScaleConc(sets, p);

  if (dataTypes & SURFACE)
    if (cnt++ == idx)
      AutoScaleSurface(sets, p);

  if (dataTypes & VOLUME)
    if (cnt++ == idx)
      AutoScaleVolume(sets, p);

}	/* END AUTOSCALE */

/* -------------------------------------------------------------------- */
void PlotInfo::ResizeX()
{
  int	lv, rv, th, bh, tv;

  x.titleOffset = 45;
  x.subTitleOffset = 65;

  lv = (int)(canvas.Width() * 0.15);
  rv = (int)(canvas.Width() * 0.9);
 
  if (nCols > 1 && plotType == XY)
    rv = lv + ((rv - lv) / nCols);

  if (plotType == XYZ)
    rv -= (int)((rv-lv) * 0.4);

  tv = canvas.Height() - 160;

  for (int i = 0; i < nPanels; ++i)
    {
    if (nPanels == 1)
      {
      th = (int)(canvas.Height() * 0.2);
      bh = (int)(canvas.Height() * 0.8);
      }
    else
      {
      th = 80 + tv / nPanels * i;
      bh = th + tv / nPanels - 50;
      }

    if (plotType == XYZ)
      th += (int)((bh-th) * 0.35);

    if (nRows > 1 && plotType == XY)
      bh = th + ((bh - th) / nRows);

    panel[i]->SetSizeX(*this, th, bh, lv, rv);
    }


  x.xLabelOffset = 40;
  x.yLabelOffset = 15;

  x.yTicLabelOffset = 5;
  x.xTicLabelOffset = 20;

}	/* END RESIZEX */

/* -------------------------------------------------------------------- */
void PlotInfo::ResizePS()
{
  int	lv, rv, th, bh, tv, tm;

  lv = (int)(printerSetup->Width() * 0.15);
  rv = (int)(printerSetup->Width() * 0.9);

  if (nCols > 1 && plotType == XY)
    rv = lv + ((rv - lv) / nCols);

  if (plotType == XYZ)
    rv -= (int)((rv-lv) * 0.4);

  tv = (int)(printerSetup->Height() * 0.75);
  tm = (int)(printerSetup->Height() * 0.15);

  for (int i = 0; i < nPanels; ++i)
    {
    if (nPanels == 1)
      {
      th = (int)(printerSetup->Height() * 0.8);
      bh = (int)(printerSetup->Height() * 0.2);
      }
    else
      {
      th = printerSetup->Height() - (tm + tv / nPanels * i);
      bh = th - (tv / nPanels - 200);
      }

    if (plotType == XYZ)
      th += (int)((th - bh) * 0.35);

    if (nRows > 1 && plotType == XY)
      bh = th - ((th - bh) / nRows);

    panel[i]->SetSizePS(*this, th, bh, lv, rv);
    }

  if (printerSetup->Shape() == Printer::LANDSCAPE)
    {
    ps.titleOffset = (int)(2250 * printerSetup->HeightRatio());
    ps.subTitleOffset = (int)(2170 * printerSetup->HeightRatio());
    }
  else
    {
    ps.titleOffset = (int)(3000 * printerSetup->HeightRatio());
    ps.subTitleOffset = (int)(2920 * printerSetup->HeightRatio());
    }

  ps.xLabelOffset = (int)(160 * printerSetup->FontRatio());
  ps.yLabelOffset = (int)(160 * printerSetup->FontRatio());

  ps.yTicLabelOffset = (int)(-20 * printerSetup->FontRatio());
  ps.xTicLabelOffset = (int)(-80 * printerSetup->FontRatio());

  ps.ticLength = (int)(25  * printerSetup->FontRatio());

}	/* END RESIZEPS */

/* -------------------------------------------------------------------- */
void PlotInfo::Draw()
{
  int		idx = 0;

  UpdateSubtitle(sets.FirstSet());
  canvas.Clear();

  if (!dataTypes)
    return;

  drawTitles(0);
  colorPen.SetLineWidth(lineWidth);

  if (dataTypes & COUNTS)
    {
    AutoScaleAccum(sets, panel[idx]);
    SetDefaultTics(idx);

    panel[idx]->DrawPlotFrames(*this);
    drawHistograms(COUNTS, idx++);
    }

  if (dataTypes & CONCENTRATION)
    {
    AutoScaleConc(sets, panel[idx]);
    SetDefaultTics(idx);

    panel[idx]->DrawPlotFrames(*this);
    drawHistograms(CONCENTRATION, idx++);
    }

  if (dataTypes & SURFACE)
    {
    AutoScaleSurface(sets, panel[idx]);
    SetDefaultTics(idx);

    panel[idx]->DrawPlotFrames(*this);
    drawHistograms(SURFACE, idx++);
    }

  if (dataTypes & VOLUME)
    {
    AutoScaleVolume(sets, panel[idx]);
    SetDefaultTics(idx);

    panel[idx]->DrawPlotFrames(*this);
    drawHistograms(VOLUME, idx++);
    }

  drawLegend(0);

  UpdateASCII();
  UpdateVars();

  canvas.ExposeAll();

}	/* END DRAW */

/* -------------------------------------------------------------------- */
void PlotInfo::Print(char *name)
{
  int	idx = 0;

  PostScript pen(name, "ncpp", title, 0.25);

  ResizePS();
  printTitles(pen);

  if (dataTypes & COUNTS)
    {
    panel[idx]->PrintPlotFrames(*this, pen);
    printHistograms(pen, COUNTS, idx++);
    }

  if (dataTypes & CONCENTRATION)
    {
    panel[idx]->PrintPlotFrames(*this, pen);
    printHistograms(pen, CONCENTRATION, idx++);
    }

  if (dataTypes & SURFACE)
    {
    panel[idx]->PrintPlotFrames(*this, pen);
    printHistograms(pen, SURFACE, idx++);
    }

  if (dataTypes & VOLUME)
    {
    panel[idx]->PrintPlotFrames(*this, pen);
    printHistograms(pen, VOLUME, idx++);
    }

  printLegend(pen);

}	/* END PRINT */

/* -------------------------------------------------------------------- */
void PlotInfo::printTitles(PostScript& pen)
{
  int offset = panel[0]->dimsPS.LV + ((panel[0]->dimsPS.HD * nCols) >> 1);

  if (title.length())
    {
    pen.SetFont(80);
    sprintf(buffer, "%d (%s) stringwidth pop 2 div sub %d moveto\n",
		offset, title.c_str(), ps.titleOffset);
    pen.Issue(buffer);

    pen.ShowStr(title);
    }

  if (subTitle.length())
    {
    pen.SetFont(60);
    sprintf(buffer, "%d (%s) stringwidth pop 2 div sub %d moveto\n",
		offset, subTitle.c_str(), ps.subTitleOffset);
    pen.Issue(buffer);

    pen.ShowStr(subTitle);
    }

}	/* END PRINTTITLES */

/* -------------------------------------------------------------------- */
void PlotInfo::drawTitles(int sizeOffset)
{
  int	offset, fontIdx;
  static char *helpURL = "http://raf.atd.ucar.edu/Software/ncpp.html";


  blackPen.DrawText(canvas.Surface(), 300, 15, helpURL);

  if (title.length() > 0)
    {
    fontIdx = XFonts::Point24 + sizeOffset;

    blackPen.SetFont(fonts.Font(fontIdx));

    offset = panel[0]->dimsX.LV + ((panel[0]->dimsX.HD * nCols) >> 1) -
		(fonts.StringWidth(fontIdx, title) >> 1);

    blackPen.DrawText(canvas.Surface(), offset, x.titleOffset, title);
    }


  if (subTitle.length() > 0)
    {
    fontIdx = XFonts::Point18 + sizeOffset;

    blackPen.SetFont(fonts.Font(fontIdx));

    offset = panel[0]->dimsX.LV + ((panel[0]->dimsX.HD * nCols) >> 1) -
		(fonts.StringWidth(fontIdx, subTitle) >> 1);

    blackPen.DrawText(canvas.Surface(), offset, x.subTitleOffset, subTitle);
    }

}	/* END DRAWTITLES */

/* -------------------------------------------------------------------- */
void PlotInfo::drawLegend(int sizeOffset)
{
  int		idx, ylegend;
  DataSet	*set;

  int	fontIdx = XFonts::Point12 - sizeOffset;
  blackPen.SetFont(fonts.Font(fontIdx));

  if (color)
    colors.ResetColors();
  else
    colorPen.SetColor(0);

  colorPen.SetLineWidth(3);

  for (idx = 0, set = sets.FirstSet(); set; set = sets.NextSet(), ++idx)
    {
    ylegend = canvas.Height() - 10 - (idx * 12);

    if (color)
      colorPen.SetColor(colors.NextColor());

    colorPen.DrawLine(canvas.Surface(), 12, ylegend-2, 50, ylegend-2);
    blackPen.DrawText(canvas.Surface(), 55, ylegend+3, set->probe->Name());

    if (!color)
      colorPen.SetDash(idx);
    }

}	/* END DRAWLEGEND */

/* -------------------------------------------------------------------- */
void PlotInfo::printLegend(PostScript& pen)
{
  int		idx, ylegend;
  DataSet	*set;

  pen.SetFont(50);

  if (printerSetup->Color())
    colors.ResetColors();

  pen.SetLineWidth(4);

  for (idx = 0, set = sets.FirstSet(); set; set = sets.NextSet(), ++idx)
    {
    ylegend = (int)((idx + 4) * 40 * printerSetup->FontRatio())+5;

    if (printerSetup->Color())
      pen.SetColor(colors.NextColorPS());

    pen.MoveTo(50, ylegend+4);
    pen.LineTo(170, ylegend+4);
    pen.MoveTo(180, ylegend);
    pen.ShowStr(set->probe->Name());

    if (!printerSetup->Color())
      pen.SetDash(idx);
    }

  if (!printerSetup->Color())
    pen.ClearDash();

}	/* END PRINTLEGEND */

/* -------------------------------------------------------------------- */
void PlotInfo::drawHistograms(DataType dt, int idx)
{
  int		row, col, cnt, n, sn;
  DataSet	*set;

  for (row = 0, cnt = 0; row < nRows; ++row)
    {
    for (col = 0; col < nCols; ++col, ++cnt)
      {
      if (color)
        colors.ResetColors();
      else
        colorPen.SetColor(0);

      colorPen.ClearDash();

      for (n = 0, set = sets.FirstSet(); set; set = sets.NextSet(), ++n)
        {
        if (color)
          colorPen.SetColor(colors.NextColor());

        sn = ditc ? n : -1;
        panel[idx]->DrawHistogram(set, sn, cnt, dt, canvas.Surface(), colorPen);

        if (!color)
          colorPen.SetDash(n);
        }

      if (plotType == XY)
        panel[idx]->IncrementColumn(1);
      else
        panel[idx]->IncrementXYZPos(nRows * nCols);
      }

    if (plotType == XY)
      {
      panel[idx]->IncrementRow(1);
      panel[idx]->DecrementColumn(nCols);
      }
    }

  if (plotType == XY)
    panel[idx]->DecrementRow(nRows);
  else
    panel[idx]->DecrementXYZPos(nRows * nCols);

}	/* END DRAWHISTOGRAM */

/* -------------------------------------------------------------------- */
void PlotInfo::printHistograms(PostScript& pen, DataType dt, int idx)
{
  int		row, col, cnt, pn;
  DataSet	*set;

  pen.SetLineWidth(lineWidth << 1);

  for (row = 0, cnt = 0; row < nRows; ++row)
    {
    for (col = 0; col < nCols; ++col, ++cnt)
      {
      if (printerSetup->Color())
        colors.ResetColors();

      for (pn = 0, set = sets.FirstSet(); set; set = sets.NextSet(), ++pn)
        {
        if (printerSetup->Color())
          pen.SetColor(colors.NextColorPS());

        panel[idx]->PrintHistogram(set, pn, cnt, dt, pen);

        if (!printerSetup->Color())
          pen.SetDash(pn);
        }

      if (!printerSetup->Color())
        pen.ClearDash();

      if (plotType == XY)
        panel[idx]->IncrementColumn(1);
      else
        panel[idx]->IncrementXYZPos(nRows * nCols);
      }

    if (plotType == XY)
      {
      panel[idx]->IncrementRow(1);
      panel[idx]->DecrementColumn(nCols);
      }
    }

  if (plotType == XY)
    panel[idx]->DecrementRow(nRows);
  else
    panel[idx]->DecrementXYZPos(nRows * nCols);

}	/* END PRINTHISTOGRAM */

/* -------------------------------------------------------------------- */
void PlotInfo::insertPanel(int pos)
{
  for (int i = nPanels; i > pos; --i)
    panel[i] = panel[i-1];
 
  panel[pos] = new Panel();
  ++nPanels;

}
 
/* -------------------------------------------------------------------- */
void PlotInfo::deletePanel(int pos)
{
  delete panel[pos];
 
  for (int i = pos; i < nPanels; ++i)
    panel[i] = panel[i+1];
 
  --nPanels;

}

/* END PLOTINFO.CC */
