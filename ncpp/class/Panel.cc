/*
-------------------------------------------------------------------------
OBJECT NAME:	Panel.cc

FULL NAME:	Panel Information/Parameters

ENTRY POINTS:	Panel()

STATIC FNS:	

DESCRIPTION:	

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-8
-------------------------------------------------------------------------
*/

#include "Panel.h"
#include "PlotInfo.h"

#include <cmath>

/* -------------------------------------------------------------------- */
Panel::Panel()
{
  AutoLabels = true;
  AutoScale = true;
  AutoTics = true;

  xAxis.logScale = yAxis.logScale = zAxis.logScale = true;
  xAxis.invertAxis = yAxis.invertAxis = zAxis.invertAxis = false;

  xAxis.nMajorTics = yAxis.nMajorTics = zAxis.nMajorTics = 4;
  xAxis.nMinorTics = yAxis.nMinorTics = zAxis.nMinorTics = 2;

  xAxis.min = yAxis.min = zAxis.min = 0.0;
  xAxis.max = yAxis.max = zAxis.max = 10.0;

  xAxis.label = "Diameter (um)";
  xAxis.label[10] = 0xb5;	// Greek mu.

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void Panel::SetSizeX(PlotInfo& plot, int th, int bh, int lv, int rv)
{
  dimsX.TH = th; dimsX.BH = bh; dimsX.LV = lv; dimsX.RV = rv;

  dimsX.HD = rv - lv;
  dimsX.VD = bh - th;

  plot.x.ticLength = dimsX.HD > 400 ? 10 : 5;

  dimsX.ZD = (int)(cosFactor * dimsX.HD);

}	/* END SETSIZEX */

/* -------------------------------------------------------------------- */
void Panel::SetSizePS(PlotInfo& plot, int th, int bh, int lv, int rv)
{
  dimsPS.TH = th; dimsPS.BH = bh; dimsPS.LV = lv; dimsPS.RV = rv;

  dimsPS.HD = rv - lv;
  dimsPS.VD = th - bh;

  dimsPS.ZD = (int)(dimsPS.HD * cosFactor);

}	/* END SETSIZEPS */

/* -------------------------------------------------------------------- */
void Panel::IncrementRow(int n)
{
  dimsX.TH += dimsX.VD * n;
  dimsX.BH += dimsX.VD * n;

  dimsPS.TH -= dimsPS.VD * n;
  dimsPS.BH -= dimsPS.VD * n;
}

/* -------------------------------------------------------------------- */
void Panel::IncrementColumn(int n)
{
  dimsX.LV += dimsX.HD * n;
  dimsX.RV += dimsX.HD * n;

  dimsPS.LV += dimsPS.HD * n;
  dimsPS.RV += dimsPS.HD * n;
}

/* -------------------------------------------------------------------- */
void Panel::DecrementColumn(int n)
{
  dimsX.LV -= dimsX.HD * n;
  dimsX.RV -= dimsX.HD * n;

  dimsPS.LV -= dimsPS.HD * n;
  dimsPS.RV -= dimsPS.HD * n;
}

/* -------------------------------------------------------------------- */
void Panel::DecrementRow(int n)
{
  dimsX.TH -= dimsX.VD * n;
  dimsX.BH -= dimsX.VD * n;

  dimsPS.TH += dimsPS.VD * n;
  dimsPS.BH += dimsPS.VD * n;
}

/* -------------------------------------------------------------------- */
void Panel::IncrementXYZPos(int n)
{
  int	offset = dimsX.ZD / n;

  dimsX.LV += offset;
  dimsX.RV += offset;
  dimsX.TH -= offset;
  dimsX.BH -= offset;
}

/* -------------------------------------------------------------------- */
void Panel::DecrementXYZPos(int n)
{
  dimsX.LV -= dimsX.ZD;
  dimsX.RV -= dimsX.ZD;
  dimsX.TH += dimsX.ZD;
  dimsX.BH += dimsX.ZD;
}

/* -------------------------------------------------------------------- */
void Panel::DrawPlotFrames(PlotInfo& plot)
{
  panelDims	saveDims = dimsX;

  if (plot.plotType == XYZ)
    {
    draw3dCube(plot.canvas.Surface(), plot.blackPen);
    drawLabels(plot);
    xTicsLabelsX(plot, true);
    yTicsLabelsX(plot, true);
    return;
    }

  drawLabels(plot);

  for (int row = 0; row < plot.nRows; ++row)
    {
    dimsX.TH += dimsX.VD * row;
    dimsX.BH += dimsX.VD * row;

    for (int col = 0; col < plot.nCols; ++col)
      {
      plot.blackPen.DrawRectangle(plot.canvas.Surface(),
				dimsX.LV, dimsX.TH, dimsX.HD, dimsX.VD);

      xTicsLabelsX(plot, col == 0 && row == plot.nRows-1);
      yTicsLabelsX(plot, col == 0 && row == 0);

      dimsX.LV += dimsX.HD;
      dimsX.RV += dimsX.HD;
      }

    dimsX = saveDims;
    }

}	/* END DRAWPLOTFRAMES */

/* -------------------------------------------------------------------- */
void Panel::PrintPlotFrames(PlotInfo& plot, PostScript& pen)
{
  panelDims	saveDims = dimsPS;

  pen.Issue("stroke 0 0 0 setrgbcolor\n");
  printLabels(plot, pen);
  pen.Issue("gsave\n");
  pen.SetLineWidth(2);

  pen.MoveOrigin(dimsPS.LV, dimsPS.BH);

  for (int row = 0; row < plot.nRows; ++row)
    {
    dimsPS.TH -= dimsPS.VD * row;
    dimsPS.BH -= dimsPS.VD * row;

    for (int col = 0; col < plot.nCols; ++col)
      {
      pen.DrawBox(0, dimsPS.VD, dimsPS.HD, 0);

      xTicsLabelsPS(plot, pen, col == 0 && row == plot.nRows-1);
      yTicsLabelsPS(plot, pen, col == 0 && row == 0);

      dimsPS.LV += dimsPS.HD;
      dimsPS.RV += dimsPS.HD;
      pen.MoveOrigin(dimsPS.HD, 0);
      }

    pen.MoveOrigin(-(plot.nCols * dimsPS.HD), -dimsPS.VD);
    dimsPS = saveDims;
    }

  pen.Issue("grestore\n");

}	/* END PRINTPLOTFRAMES */

/* -------------------------------------------------------------------- */
void Panel::printLabels(PlotInfo& plot, PostScript& pen)
{
  pen.SetFont(60);

  if (xAxis.label.length() > 0)
    {
    sprintf(buffer, "%d (%s) stringwidth pop 2 div sub %d moveto\n",
	dimsPS.LV + ((dimsPS.HD * plot.nCols) >> 1),
	xAxis.label.c_str(),
	dimsPS.TH - (dimsPS.VD * plot.nRows) - plot.ps.xLabelOffset);

    pen.Issue(buffer);
    pen.ShowStr(xAxis.label);
    }

  if (yAxis.label.length() > 0)
    {
    sprintf(buffer, "%d (%s) stringwidth pop 2 div sub %d moveto\n",
	dimsPS.LV - plot.ps.yLabelOffset,
	yAxis.label.c_str(),
	dimsPS.TH - ((dimsPS.VD * plot.nRows) >> 1));

    pen.Issue(buffer);
    pen.Rotate(90);
    pen.ShowStr(yAxis.label);
    pen.Rotate(-90);
    }

}	/* END PRINTLABELS */

/* -------------------------------------------------------------------- */
void Panel::drawLabels(PlotInfo& plot)
{
  int		xOffset, yOffset;

  const XFontStruct	*fontInfo = plot.fonts.Font(XFonts::Point18);

  int ascent	= fontInfo->max_bounds.ascent;
  int charSize	= ascent + fontInfo->max_bounds.descent;

  plot.blackPen.SetFont(fontInfo);


  if (xAxis.label.length() > 0)
    {
    xOffset = dimsX.LV + ((dimsX.HD * plot.nCols) >> 1) -
		(plot.fonts.StringWidth(fontInfo, xAxis.label) >> 1);

    yOffset = dimsX.TH + (dimsX.VD * plot.nRows) + plot.x.xLabelOffset;

    plot.blackPen.DrawText(plot.canvas.Surface(), xOffset,yOffset, xAxis.label);
    }


  if (yAxis.label.length() > 0)
    {
    PixMap	in_pm(plot.canvas.Wdgt(), 300, 30),
		out_pm(plot.canvas.Wdgt(), 30, 300);

    xOffset = plot.x.yLabelOffset;

    int pixLen = plot.fonts.StringWidth(fontInfo, yAxis.label);

    /* Create a pixmap, draw string to it and read it back out as an Image.
     */
    in_pm.Clear();
    plot.blackPen.DrawText(in_pm.Surface(), 0, ascent, yAxis.label);

    XImage *im_in = in_pm.GetImage(pixLen, charSize);
    XImage *im_out = out_pm.GetImage(charSize, pixLen);


    /* Rotate pixmap
     */
    for (int i = 0; i < charSize; i++)
      for (int j = 0; j < pixLen; j++)
        XPutPixel(im_out, i, pixLen-j-1, XGetPixel(im_in, j, i));

    /* Write out the rotated text
     */
    yOffset = dimsX.TH + ((dimsX.VD * plot.nRows) >> 1) - (pixLen >> 1);

    plot.canvas.PutImage(im_out, xOffset, yOffset, charSize, pixLen);
    XDestroyImage(im_in);
    XDestroyImage(im_out);
    }


  /* Z label.
   */
  if (plot.plotType == XYZ && zAxis.label.length() > 0)
    {
    plot.blackPen.DrawText(plot.canvas.Surface(),
		dimsX.RV + 100, dimsX.BH - 20, zAxis.label);
    }

}	/* END PLOTLABELS */

/* -------------------------------------------------------------------- */
void Panel::yTicsLabelsX(PlotInfo& plot, bool labels)
{
  int		xoffset, yoffset, ticlen, minorTicLen, logFac = 0;
  double	nMajorYpix, nMinorYpix;
  double	yDiff, value;
  std::string	ticLabel;
  Drawable	surface = plot.canvas.Surface();
  XPen		pen = plot.blackPen;

  const XFontStruct	*fontInfo = plot.fonts.Font(plot.nRows > 1 ? XFonts::Point10 : XFonts::Point12);

  pen.SetFont(fontInfo);

  /* Draw Y-axis tic marks and #'s
   */
  if (plot.grid)
    ticlen = minorTicLen = dimsX.HD;
  else
    {
    ticlen = plot.x.ticLength;
    minorTicLen = ticlen * 2 / 3;
    }

  if (yAxis.logScale && plot.nRows > 1)
    minorTicLen = plot.x.ticLength * 2 / 3;

  yDiff		= yAxis.max - yAxis.min;
  nMajorYpix	= (double)dimsX.VD / yAxis.nMajorTics;
  nMinorYpix	= nMajorYpix / yAxis.nMinorTics;

  for (int i = 0; i <= yAxis.nMajorTics; ++i)
    {
    if (yAxis.invertAxis)
      yoffset = dimsX.TH + (int)(i * nMajorYpix);
    else
      yoffset = dimsX.BH - (int)(i * nMajorYpix);

    if (yoffset < dimsX.TH)
      yoffset = dimsX.TH;

    pen.DrawLine(surface, dimsX.LV, yoffset, dimsX.LV + ticlen, yoffset);

    if (!plot.grid)
      pen.DrawLine(surface, dimsX.RV - ticlen, yoffset, dimsX.RV, yoffset);

    if (labels)
      {
      if (yAxis.logScale)
        {
        ticLabel = MakeLogTicLabel(yAxis.min * pow(10.0, (double)logFac));

        ++logFac;
        }
      else
        {
        value = yAxis.min + (yDiff / yAxis.nMajorTics * i);
        ticLabel = MakeTicLabel(yDiff, yAxis.nMajorTics, value);
        }

      xoffset = dimsX.LV - plot.x.yTicLabelOffset -
			plot.fonts.StringWidth(fontInfo, ticLabel);

      pen.DrawText(surface, xoffset, yoffset+4, ticLabel);
      }

    if (i != yAxis.nMajorTics)
      {
      for (int j = 1; j < yAxis.nMinorTics; ++j)
        {
        if (yAxis.invertAxis)
          {
          yoffset = dimsX.TH + (int)(nMajorYpix * i);
          if (yAxis.logScale)
            yoffset += (int)(log10((double)j) * nMajorYpix);
          else
            yoffset += (int)(nMinorYpix * j);
          }
        else
          {
          yoffset = dimsX.BH - (int)(nMajorYpix * i);
          if (yAxis.logScale)
            yoffset -= (int)(log10((double)j) * nMajorYpix);
          else
            yoffset -= (int)(nMinorYpix * j);
          }


        pen.DrawLine(surface, dimsX.LV, yoffset,
				dimsX.LV + minorTicLen, yoffset);
        if (!plot.grid && plot.nRows == 1)
          pen.DrawLine(surface, dimsX.RV, yoffset,
				dimsX.RV - minorTicLen, yoffset);
        }
      }
    }

}	/* END YTICSLABELSX */

/* -------------------------------------------------------------------- */
void Panel::xTicsLabelsX(PlotInfo& plot, bool labels)
{
  int		ticlen, minorTicLen, offset, logFac = 0;
  double	nMajorXpix, nMinorXpix;
  double	xDiff, value;
  std::string	ticLabel;
  Drawable	surface = plot.canvas.Surface();
  XPen		pen = plot.blackPen;

  const XFontStruct	*fontInfo = plot.fonts.Font(plot.nRows > 1 ? XFonts::Point10 : XFonts::Point12);

  pen.SetFont(fontInfo);


  /* Draw X-axis tic marks and #'s
   */
  if (plot.grid)
    ticlen = minorTicLen = dimsX.VD;
  else
    {
    ticlen = plot.x.ticLength;
    minorTicLen = ticlen * 2 / 3;
    }

  if (xAxis.logScale && plot.nRows > 1)
    minorTicLen = plot.x.ticLength * 2 / 3;

  nMajorXpix	= (double)dimsX.HD / xAxis.nMajorTics;
  nMinorXpix	= (double)nMajorXpix / xAxis.nMinorTics;
  xDiff		= xAxis.max - xAxis.min;

  for (int i = 0; i <= xAxis.nMajorTics; ++i)
    {
    if (xAxis.invertAxis)
      offset = dimsX.RV - (int)(nMajorXpix * i + 0.5);
    else
      offset = dimsX.LV + (int)(nMajorXpix * i + 0.5);

    if (offset > dimsX.RV)
      offset = dimsX.RV;

    pen.DrawLine(surface, offset, dimsX.BH, offset, dimsX.BH - ticlen);

    if (!plot.grid)
      pen.DrawLine(surface, offset, dimsX.TH, offset, dimsX.TH + ticlen);


    if (labels)
      {
      if (xAxis.logScale)
        {
        ticLabel = MakeLogTicLabel(xAxis.min * pow(10.0, (double)logFac));

        ++logFac;
        }
      else
        {
        value = xAxis.min + (xDiff / xAxis.nMajorTics * i);
        ticLabel = MakeTicLabel(xDiff, xAxis.nMajorTics, value);
        }

      offset -= (plot.fonts.StringWidth(fontInfo, ticLabel) >> 1);
      pen.DrawText(surface, offset, dimsX.BH+plot.x.xTicLabelOffset, ticLabel);
      }

    if (i != xAxis.nMajorTics)
      {
      for (int j = 1; j < xAxis.nMinorTics; ++j)
        {
        if (xAxis.invertAxis)
          {
          offset = dimsX.RV - (int)(nMajorXpix * i);
          if (xAxis.logScale)
            offset -= (int)(log10((double)j) * nMajorXpix);
          else
            offset -= (int)(nMinorXpix * j);
          }
        else
          {
          offset = dimsX.LV + (int)(nMajorXpix * i);
          if (xAxis.logScale)
            offset += (int)(log10((double)j) * nMajorXpix);
          else
            offset += (int)(nMinorXpix * j);
          }


        pen.DrawLine(surface, offset, dimsX.BH, offset, dimsX.BH - minorTicLen);

        if (!plot.grid && plot.nRows == 1)
          pen.DrawLine(surface, offset, dimsX.TH, offset, dimsX.TH+minorTicLen);
        }
      }
    }

}	/* END XTICSLABELSX */

/* -------------------------------------------------------------------- */
void Panel::yTicsLabelsPS(PlotInfo& plot, PostScript& pen, bool labels)
{
  int		y, logFac = 0;
  int		ticlen, minorTicLen;
  float		nMajorYpix, nMinorYpix;
  std::string	ticLabel;
  double	value, yDiff;

  pen.SetFont(50);
  pen.SetLineWidth(1);

  /* Draw Y-axis tic marks & corresponding values
   */
  if (plot.grid)
    ticlen = minorTicLen = dimsPS.HD;
  else
    {
    ticlen = plot.ps.ticLength;
    minorTicLen = ticlen * 2 / 3;
    }

  if (yAxis.logScale && plot.nRows > 1)
    minorTicLen = plot.ps.ticLength * 2 / 3;


  yDiff         = yAxis.max - yAxis.min;
  nMajorYpix    = (double)dimsPS.VD / yAxis.nMajorTics;
  nMinorYpix    = nMajorYpix / yAxis.nMinorTics;

  for (int i = 0; i <= yAxis.nMajorTics; ++i)
    {
    if (yAxis.invertAxis)
      y = dimsPS.VD - (int)(nMajorYpix * i + 0.5);
    else
      y = (int)(nMajorYpix * i + 0.5);

    pen.MoveTo(0, y);
    pen.LineTo(ticlen, y);

    if (!plot.grid && plot.plotType != XYZ)
      {
      pen.MoveTo(dimsPS.HD - ticlen, y);
      pen.LineTo(dimsPS.HD, y);
      }


    if (labels)
      {
      if (yAxis.logScale)
        {
        ticLabel = MakeLogTicLabel(yAxis.min * pow(10.0, (double)logFac));

        ++logFac;
        }
      else
        {
        value = yAxis.min + (yDiff / yAxis.nMajorTics * i);
        ticLabel = MakeTicLabel(yDiff, yAxis.nMajorTics, value);
        }

      sprintf(buffer, "%d (%s) stringwidth pop sub %d moveto\n",
	plot.ps.yTicLabelOffset, ticLabel.c_str(), y-10);
      pen.Issue(buffer);
      pen.ShowStr(ticLabel);
      }


    // Minor Tic marks.
    if (i != yAxis.nMajorTics)
      for (int j = 1; j < yAxis.nMinorTics; ++j)
        {
        if (yAxis.invertAxis)
          {
          y = dimsPS.VD - (int)(nMajorYpix * i);

          if (yAxis.logScale)
            y -= (int)(log10((double)j) * nMajorYpix);
          else
            y -= (int)(nMinorYpix * j);
          }
        else
          {
          y = (int)(nMajorYpix * i);

          if (yAxis.logScale)
            y += (int)(log10((double)j) * nMajorYpix);
          else
            y += (int)(nMinorYpix * j);
          }

        pen.MoveTo(0, y);
        pen.LineTo(minorTicLen, y);

        if (!plot.grid && plot.nRows == 1)
          {
          pen.MoveTo(dimsPS.HD - minorTicLen, y);
          pen.LineTo(dimsPS.HD, y);
          }
        }
    }

  pen.Stroke();

}	/* END PSYTICS */

/* -------------------------------------------------------------------- */
void Panel::xTicsLabelsPS(PlotInfo& plot, PostScript& pen, bool labels)
{
  int		x, logFac = 0;
  int		ticlen, minorTicLen;
  float		nMajorXpix, nMinorXpix;
  std::string	ticLabel;
  double	value, xDiff;

  pen.SetFont(50);
  pen.SetLineWidth(1);

  if (plot.grid)
    ticlen = minorTicLen = dimsPS.VD;
  else
    {
    ticlen = plot.ps.ticLength;
    minorTicLen = ticlen * 2 / 3;
    }

  if (yAxis.logScale && plot.nRows > 1)
    minorTicLen = plot.ps.ticLength * 2 / 3;


  xDiff         = xAxis.max - xAxis.min;
  nMajorXpix    = (double)dimsPS.HD / xAxis.nMajorTics;
  nMinorXpix    = nMajorXpix / xAxis.nMinorTics;


  for (int i = 0; i <= xAxis.nMajorTics; ++i)
    {
    if (xAxis.invertAxis)
      x = dimsPS.HD - (int)(nMajorXpix * i + 0.5);
    else
      x = (int)(nMajorXpix * i + 0.5);

    pen.MoveTo(x, 0);
    pen.LineTo(x, ticlen);

    if (!plot.grid && plot.plotType != XYZ)
      {
      pen.MoveTo(x, dimsPS.VD - ticlen);
      pen.LineTo(x, dimsPS.VD);
      }


    if (labels)
      {
      if (xAxis.logScale)
        {
        ticLabel = MakeLogTicLabel(xAxis.min * pow(10.0, (double)logFac));
        ++logFac;
        }
      else
        {
        value = xAxis.min + (xDiff / xAxis.nMajorTics * i);
        ticLabel = MakeTicLabel(xDiff, xAxis.nMajorTics, value);
        }

      sprintf(buffer, "%d (%s) stringwidth pop 2 div sub %d moveto\n",
	x, ticLabel.c_str(), plot.ps.xTicLabelOffset);
      pen.Issue(buffer);
      pen.ShowStr(ticLabel);
      }


    // Minor Tic marks.
    if (i != xAxis.nMajorTics)
      for (int j = 1; j < xAxis.nMinorTics; ++j)
        {
        if (xAxis.invertAxis)
          {
          x = dimsPS.HD - (int)(nMajorXpix * i);

          if (xAxis.logScale)
            x -= (int)(log10((double)j) * nMajorXpix);
          else
            x -= (int)(nMinorXpix * j);
          }
        else
          {
          x = (int)(nMajorXpix * i);

          if (xAxis.logScale)
            x += (int)(log10((double)j) * nMajorXpix);
          else
            x += (int)(nMinorXpix * j);
          }

        pen.MoveTo(x, 0);
        pen.LineTo(x, minorTicLen);

        if (!plot.grid && plot.nRows == 1)
          {
          pen.MoveTo(x, dimsPS.VD - minorTicLen);
          pen.LineTo(x, dimsPS.VD);
          }
        }
    }

  pen.Stroke();

}	/* END PSXTICS */

/* -------------------------------------------------------------------- */
void Panel::draw3dCube(Drawable surface, XPen& pen)
{
  XPoint        pts[8];

  pts[0].x = dimsX.LV;
  pts[0].y = dimsX.TH;
  pts[1].x = dimsX.LV;
  pts[1].y = dimsX.BH;
  pts[2].x = dimsX.RV;
  pts[2].y = dimsX.BH;

  pts[3].x = pts[2].x + (int)(cosFactor * dimsX.ZD);
  pts[3].y = pts[2].y - (int)(sinFactor * dimsX.ZD);

  pts[4].x = pts[3].x - dimsX.HD;
  pts[4].y = pts[3].y;

  pts[5].x = dimsX.LV;
  pts[5].y = dimsX.BH;

  pen.DrawLines(surface, pts, 6);

  pts[1].x = pts[0].x + (int)(cosFactor * dimsX.ZD);
  pts[1].y = pts[0].y - (int)(sinFactor * dimsX.ZD);

  pts[2].x = pts[1].x + dimsX.HD;
  pts[2].y = pts[1].y;

  pts[5].x = pts[4].x;
  pts[5].y = pts[4].y - dimsX.VD;

  pen.DrawLines(surface, pts, 6);

}	/* END DRAW3DCUBE */

/* -------------------------------------------------------------------- */
void Panel::DrawHistogram(DataSet *set, int setNum, int idx, DataType dt, Drawable surface, XPen& pen)
{
  int		nPts = 0;
  XPoint	pts[600];
  double	datumX, datumY, xMin, xMax, yMin, yMax, total = 0.0;

  xMin = xAxis.logScale ? log10(xAxis.min) : xAxis.min;
  yMin = yAxis.logScale ? log10(yAxis.min) : yAxis.min;
  xMax = xAxis.logScale ? log10(xAxis.max) : xAxis.max;
  yMax = yAxis.logScale ? log10(yAxis.max) : yAxis.max;

  double xScale = (double)dimsX.HD / (xMax - xMin);
  double yScale = (double)dimsX.VD / (yMax - yMin);

  for (int i = set->probe->FirstBin(); i <= set->probe->LastBin(); ++i)
    {
    datumX = set->probe->CellSize(i-1);

    switch (dt)
      {
      case COUNTS:
        datumX = (double)i;
        datumY = set->Accumulation(idx, i);
        total += datumY;
        break;
      case CONCENTRATION:
        datumY = set->Concentration(idx, i);
        total += datumY * set->NormalizeFactor(i);
        break;
      case SURFACE:
        datumY = set->Surface(idx, i);
        total += datumY * set->NormalizeFactor(i);
        break;
      case VOLUME:
        datumY = set->Volume(idx, i);
        total += datumY * set->NormalizeFactor(i);
        break;
      }


    if (xAxis.logScale)
      datumX = log10(datumX);

    if (yAxis.logScale)
      datumY = log10(datumY);

    if (xAxis.invertAxis)
      pts[nPts].x = dimsX.RV - (int)(xScale * (datumX - xMin));
    else
      pts[nPts].x = dimsX.LV + (int)(xScale * (datumX - xMin));

    if (yAxis.invertAxis)
      pts[nPts].y = dimsX.TH + (int)(yScale * (datumY - yMin));
    else
      pts[nPts].y = dimsX.BH - (int)(yScale * (datumY - yMin));

    ++nPts;

    if (pts[nPts].y < dimsX.BH)
      pts[nPts].y = dimsX.BH;

    if (pts[nPts].y > dimsX.TH)
      pts[nPts].y = dimsX.TH;

    if (dt == COUNTS)
      datumX = (double)i + 1;
    else
      datumX = set->probe->CellSize(i);

    if (xAxis.logScale)
      datumX = log10(datumX);

    if (xAxis.invertAxis)
      pts[nPts].x = dimsX.RV - (int)(xScale * (datumX - xMin));
    else
      pts[nPts].x = dimsX.LV + (int)(xScale * (datumX - xMin));
    pts[nPts].y = pts[nPts-1].y;
    ++nPts;
    }

  pen.SetClipping(dimsX.LV, dimsX.TH, dimsX.HD, dimsX.VD);
  pen.DrawLines(surface, pts, nPts);

  if (setNum >= 0)
    {
    if (dt == COUNTS || total > 10.0)
      sprintf(buffer, "%6d", (int)total);
    else
      sprintf(buffer, "%6.3f", total);

    pen.DrawText(surface, dimsX.RV-40, dimsX.TH+15+(setNum*12), buffer);
    }

  pen.ClearClipping();
 
}	/* END DRAWHISTOGRAM */

/* -------------------------------------------------------------------- */
void Panel::PrintHistogram(DataSet *set, int setNum, int idx, DataType dt, PostScript& pen)
{
  int		x, y;
  double	datumX, datumY, xMin, xMax, yMin, yMax, total = 0.0;

  xMin = xAxis.logScale ? log10(xAxis.min) : xAxis.min;
  yMin = yAxis.logScale ? log10(yAxis.min) : yAxis.min;
  xMax = xAxis.logScale ? log10(xAxis.max) : xAxis.max;
  yMax = yAxis.logScale ? log10(yAxis.max) : yAxis.max;

  double xScale = (double)dimsPS.HD / (xMax - xMin);
  double yScale = (double)dimsPS.VD / (yMax - yMin);

  pen.MoveOrigin(dimsPS.LV, dimsPS.BH);
  pen.SetClipping(dimsPS.VD, dimsPS.HD);

  for (int i = set->probe->FirstBin(); i <= set->probe->LastBin(); ++i)
    {
    datumX = set->probe->CellSize(i-1);

    switch (dt)
      {
      case COUNTS:
        datumX = (double)i;
        datumY = set->Accumulation(idx, i);
        break;
      case CONCENTRATION:
        datumY = set->Concentration(idx, i);
        break;
      case SURFACE:
        datumY = set->Surface(idx, i);
        break;
      case VOLUME:
        datumY = set->Volume(idx, i);
        break;
      }

    total += datumY;

    if (xAxis.logScale)
      datumX = log10(datumX);

    if (yAxis.logScale)
      datumY = log10(datumY);

    if (xAxis.invertAxis)
      x = dimsPS.HD - (int)(xScale * (datumX - xMin));
    else
      x = (int)(xScale * (datumX - xMin));

    if (yAxis.invertAxis)
      {
      y = dimsPS.VD - (int)(yScale * (datumY - yMin));
      if (y < 0) y = dimsPS.VD;
      if (y > dimsPS.VD) y = 0;
      }
    else
      {
      y = (int)(yScale * (datumY - yMin));
      if (y < 0) y = 0;
      if (y > dimsPS.VD) y = dimsPS.VD;
      }

    if (i == set->probe->FirstBin())
      pen.MoveTo(x, y);
    else
      pen.LineTo(x, y);

    if (dt == COUNTS)
      datumX = (double)i + 1;
    else
      datumX = set->probe->CellSize(i);

    if (xAxis.logScale)
      datumX = log10(datumX);

    if (xAxis.invertAxis)
      x = dimsPS.HD - (int)(xScale * (datumX - xMin));
    else
      x = (int)(xScale * (datumX - xMin));
    pen.LineTo(x, y);
    }

  if (setNum >= 0)
    {
    if (dt == COUNTS || total > 10.0)
      sprintf(buffer, "%6d", (int)total);
    else
      sprintf(buffer, "%6.3f", total);

    pen.MoveTo(dimsPS.RV-35, dimsPS.TH+15);
    pen.ShowStr(buffer);
    }

  pen.ClearClipping();
  pen.MoveOrigin(-dimsPS.LV, -dimsPS.BH);
 
}	/* END PRINTHISTOGRAM */

/* END PANEL.CC */
