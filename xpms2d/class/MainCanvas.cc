/*
-------------------------------------------------------------------------
OBJECT NAME:    MainCanvas.cc
 
FULL NAME:      Main canvas
 
ENTRY POINTS:
 
DESCRIPTION:
 
REFERENCES:
 
REFERENCED BY:
 
NOTES:
 
COPYRIGHT:	University Corporation for Atmospheric Research, 1997-2003
-------------------------------------------------------------------------
*/

#include "MainCanvas.h"
#include "Enchilada.h"
#include "Colors.h"
#include "XFonts.h"
#include "XPen.h"

extern Enchilada       *enchiladaWin; 
extern Colors	*color;
extern XFonts	*fonts;
extern XPen	*pen;

#include <algorithm>

static const int	TOP_OFFSET = 35;
static const int	LEFT_MARGIN = 5;
// RAF HVPS, 40 pixels masked at each end of diode array.
static const int	HVPS_MASKED = 40;

/* -------------------------------------------------------------------- */
MainCanvas::MainCanvas(Widget w) : Canvas(w)
{
  SetDisplayMode(NORMAL);

  wrap = false;
  timingWord = true;

  reset(NULL);

}       /* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void MainCanvas::SetDisplayMode(int mode)
{
  displayMode = mode;

  switch (displayMode)
    {
    case NORMAL:
    case DIAGNOSTIC:
      PIX_PER_Y = 70;
      break;

    case ENCHILADA:
      PIX_PER_Y = 600;
      break;
    }

  maxRecs = (Height() - TOP_OFFSET) / PIX_PER_Y;

}	/* END SETDISPLAYMODE */

/* -------------------------------------------------------------------- */
void MainCanvas::reset(ADS_DataFile *file)
{
  char		buffer[256];

  maxRecs = (Height() - TOP_OFFSET) / PIX_PER_Y;
  y = TOP_OFFSET;

  if (file)
    {
    sprintf(buffer, "%s, %s - %s", file->ProjectNumber(), file->FlightNumber(),
	file->FlightDate());

    pen->SetFont(fonts->Font(0));
    pen->DrawText(Surface(), 300, 25, buffer);
    }

}	/* END RESET */

/* -------------------------------------------------------------------- */
void MainCanvas::draw(P2d_rec *record, struct recStats &stats, float version, int probeNum, PostScript *ps)
{
  int		i, j, nextColor, cntr = 0, y1, shaded, unshaded;
  ulong		*p, slice, pSlice, ppSlice, timeWord, thisTime, syncWord;
  char		buffer[256];
  bool		debug = false, colorIsBlack = False;
  Particle	*cp;

  static short  prevOverLoad = 0;
  static ulong  prevSlice[2];
  static ulong  prevTime;

  if (version < 3.35)
    syncWord = 0xff000000;
  else
    syncWord = 0x55000000;

//  if (record->msec == 397) debug = true;

  // Ok, now go back and display the data.
  p = (ulong *)record->data;
  ppSlice = prevSlice[0];
  pSlice = prevSlice[1];
  pen->SetFont(fonts->Font(3));

  thisTime = (record->hour * 3600 + record->minute * 60 + record->second)
		* 1000 + record->msec;


  if (ps) ps->SetColor(color->GetColorPS(BLACK));
  else pen->SetColor(color->GetColor(BLACK));

  if (ps) { ps->MoveTo(35, 750-(y-2)); ps->LineTo(1060, 750-(y-2)); }
  else pen->DrawLine(Surface(), 0, y-2, Width(), y-2);

  if (ps) { ps->MoveTo(547, 750-(y-5)); ps->LineTo(547, 750-y); }
  else pen->DrawLine(Surface(), 523, y-5, 523, y);


  if (((char *)&record->id)[0] == 'H')
    {
    int		line = LEFT_MARGIN;
    ushort	*sp = (ushort *)record->data;

    if (*sp == 0xcaaa)
      {
//      printf("MainCanvas:draw: diagnostic record.\n");
      return;
      }

//printf("--------------------------------\n");
    pen->SetColor(color->GetColor(RED));
//    pen->DrawLine(Surface(), line, y+HVPS_MASKED, 1600, y+HVPS_MASKED);
    pen->DrawLine(Surface(), line, y+(128-HVPS_MASKED), 1600, y+(128-HVPS_MASKED));
//    pen->DrawLine(Surface(), line, y+256-HVPS_MASKED, 1600, y+256-HVPS_MASKED);

    for (i = 0; i < 2048; )
      {
      if (wrap && line >= Width()-(LEFT_MARGIN<<1))
        {
        line = LEFT_MARGIN;
        y += 190 + PIX_PER_Y - (HVPS_MASKED<<1);

        if (ps) {
          ps->SetColor(color->GetColorPS(RED));
          }
        else {
          pen->SetColor(color->GetColor(RED));
          }

        pen->DrawLine(Surface(), line, y+(128-HVPS_MASKED), line+1500, y+(128-HVPS_MASKED));
        }

      if (sp[i] & 0x8000)
        {
//        if (!(sp[i+1] & 0x8000))
//          printf("Missaligned timing words.\n");

        if ((cp = (Particle *)stats.particles.DeQueue()) == NULL)
          break;

        line += 2;

        if (timingWord)
          {
          if (cp && cp->reject) {
            if (ps) ps->SetColor(color->GetColorPS(RED));
            else pen->SetColor(color->GetColor(RED));
            }
          else {
            if (ps) ps->SetColor(color->GetColorPS(GREEN));
            else pen->SetColor(color->GetColor(GREEN));
            }

          pen->DrawLine(Surface(), line, y, line, y+256-(HVPS_MASKED<<1));
          }

        if (ps) ps->SetColor(color->GetColorPS(BLUE));
        else pen->SetColor(color->GetColor(BLUE));

//printf("\ntiming: %d, ovrld=%x - %x", (((ulong)sp[i] << 15) & 0x3fff0000)+(ulong)(sp[i+1] & 0x3fff), sp[i] & 0xc000, sp[i+1] & 0xc000);

        i += 2;

        for (; !(sp[i] & 0x8000) && i < 2048; ++i)
          {
          shaded = (sp[i] & 0x3f80) >> 7;
          unshaded = sp[i] & 0x007f;

          if (sp[i] & 0x4000)
            {
            y1 = y;

            if (sp[i] == 0x4000)
              y1 += 128;

            line += 1;	// Max airspeed is 45 m/s.  Cheesy multiply by 2.
            unshaded -= HVPS_MASKED;
//printf("\n %4d", i);
            }

//if (sp[i] == 0x4000)
//  printf(" 128   0");
//else
//  printf(" %3d %3d", unshaded, shaded);

          if (shaded > 0)
            {	// Max airspeed is 45 m/s.  Cheesy multiply by 2.  Draw lines twice.
            pen->DrawLine(Surface(), line, y1 + unshaded,
				line, y1 + unshaded + shaded);
//            pen->DrawLine(Surface(), line + 1, y1 + unshaded,
//				line + 1, y1 + unshaded + shaded);
            }

          y1 += unshaded + shaded;
          }

        if (enchiladaWin)
          enchiladaWin->AddLineItem(cntr++, cp);

        delete cp;
        }
      else
        ++i;
      }

    y += 224 - (HVPS_MASKED<<1);
    }
  else
  for (i = 0; i < 1024; ++p)		/* 2DC and/or 2DP	*/
    {
    slice = *p;

    /* If sync word and word before is not -1, then sum up timing words
     * into milliseconds.
     */
    if (slice == syncWord && ppSlice == 0xffffffff && pSlice != 0xffffffff)
      {
      if ((cp = (Particle *)stats.particles.DeQueue()) == NULL)
        break;

if (debug) if (cp) printf("dq: %06x %d %d\n", cp->timeWord, cp->h, cp->w); else printf("NULL\n");

      timeWord = (ulong)((float)cp->timeWord * stats.frequency);

      if (timeWord >= stats.DASelapsedTime)
        {
        sprintf(buffer, "%u", timeWord);

        if (ps) {
          ps->SetColor(color->GetColorPS(RED));
          ps->MoveTo(i+10, 750-(y+(PIX_PER_Y-30)));
          ps->ShowStr(buffer);
          }
        else {
          pen->SetColor(color->GetColor(RED));
          pen->DrawText(Surface(), i+10, y+(PIX_PER_Y-30), buffer);
          }
        }


      // Draw timing & sync words in yellow (or some other color).
      if (cp && cp->reject) {
        if (cp->h == 1 && cp->w == 1)
          if (ps) ps->SetColor(color->GetColorPS(YELLOW));
          else pen->SetColor(color->GetColor(YELLOW));
        else
          if (ps) ps->SetColor(color->GetColorPS(RED));
          else pen->SetColor(color->GetColor(RED));

        nextColor = 0;
        }
      else {	// Green for good particle
        if (ps) ps->SetColor(color->GetColorPS(GREEN));
        else pen->SetColor(color->GetColor(GREEN));

        nextColor = probeNum;
        }

      if (timingWord)
        {
        drawSlice(ps, i++, pSlice);
        drawSlice(ps, i++, slice);
      }
     else
       i += 2;

      if (ps) ps->SetColor(color->GetColorPS(nextColor));
      else pen->SetColor(color->GetColor(nextColor));

      if (nextColor == 0)	// if Black
        colorIsBlack = True;
      else
        colorIsBlack = False;

      for (++p; i < 1024 && *p != 0xffffffff; ++p)
        {
        drawSlice(ps, i++, *p);
        }

      if (enchiladaWin)
        enchiladaWin->AddLineItem(cntr++, cp);

      delete cp;
      }
    else
    if (p[1] != syncWord)
      {
      if (!colorIsBlack)
        {
        if (ps) ps->SetColor(color->GetColorPS(BLACK));
        else pen->SetColor(color->GetColor(BLACK));

        colorIsBlack = True;
        }

      drawSlice(ps, i++, slice);
      }
    else
      ++i;

    ppSlice = pSlice;
    pSlice = slice;
    }


 
  if (stats.DASelapsedTime == 0)
    {
    strcpy(buffer, " DUPLICATE RECORD! ");
    if (ps)
      {
      ps->SetColor(color->GetColorPS(RED));
      ps->MoveTo(10, 750-(y+15)); ps->ShowStr(buffer);
      ps->MoveTo(300, 750-(y+15)); ps->ShowStr(buffer);
      ps->MoveTo(600, 750-(y+15)); ps->ShowStr(buffer);
      }
    else
      {
      pen->SetColor(color->GetColor(RED));
      pen->DrawText(Surface(), 10, y+15, buffer);
      pen->DrawText(Surface(), 300, y+15, buffer);
      pen->DrawText(Surface(), 600, y+15, buffer);
      }
    }

  // Draw text info at bottom of record.
  if (ps) ps->SetColor(color->GetColorPS(BLACK));
  else pen->SetColor(color->GetColor(BLACK));

  if (thisTime < prevTime) {
    if (ps) ps->SetColor(color->GetColorPS(RED));
    else pen->SetColor(color->GetColor(RED));
    }

  sprintf(buffer, "%02d:%02d:%02d.%d",
	record->hour, record->minute, record->second, record->msec);

  if (ps) {
    ps->MoveTo(200, 750-(y+50)); ps->ShowStr(buffer);
    ps->SetColor(color->GetColorPS(BLACK));
    }
  else {
    pen->DrawText(Surface(), 200, y+50, buffer);
    pen->SetColor(color->GetColor(BLACK));
    }

  sprintf(buffer, ", TAS=%5.1f, overLoad=", stats.tas);
  if (ps) { ps->MoveTo(283, 750-(y+50)); ps->ShowStr(buffer); }
  else pen->DrawText(Surface(), 283, y+50, buffer);

  if (prevOverLoad > 90) {
    if (ps) ps->SetColor(color->GetColorPS(RED));
    else pen->SetColor(color->GetColor(RED));
    }

  sprintf(buffer, "%.3f,", (float)prevOverLoad / 1000);
  if (ps) {
    ps->MoveTo(445, 750-(y+50)); ps->ShowStr(buffer);
    ps->SetColor(color->GetColorPS(BLACK));
    }
  else {
    pen->DrawText(Surface(), 445, y+50, buffer);
    pen->SetColor(color->GetColor(BLACK));
    }

  sprintf(buffer, "nParticles = %d, elapsed time = ", stats.nTimeBars);
  if (ps) { ps->MoveTo(490, 750-(y+50)); ps->ShowStr(buffer); }
  else pen->DrawText(Surface(), 490, y+50, buffer);

  if (stats.DASelapsedTime / 1000 > 36000) {
    if (ps) ps->SetColor(color->GetColorPS(RED));
    else pen->SetColor(color->GetColor(RED));

    sprintf(buffer, "%6d", stats.DASelapsedTime / 1000);
    }
  else {
    sprintf(buffer, "%6.3f", (float)stats.DASelapsedTime / 1000);
    }

  if (ps) { ps->MoveTo(706, 750-(y+50)); ps->ShowStr(buffer); }
  else pen->DrawText(Surface(), 706, y+50, buffer);

  if (ps) ps->SetColor(color->GetColorPS(BLACK));
  else pen->SetColor(color->GetColor(BLACK));

  sprintf(buffer,", timeBarTotal = %6.3f", (float)stats.tBarElapsedtime / 1000);
  if (ps) { ps->MoveTo(750, 750-(y+50)); ps->ShowStr(buffer); }
  else pen->DrawText(Surface(), 750, y+50, buffer);


  if (stats.DASelapsedTime == 0.0)
    sprintf(buffer, "%.1f%% %.1f%%", 0.0, 0.0);
  else
    {
//    float  olap =	(float)(stats.tBarElapsedtime+record->overld) /
    float  olap =	(float)(stats.tBarElapsedtime+prevOverLoad) /
			stats.DASelapsedTime * 100;

    if (olap < 75.0 || olap > 125.0) {
      if (ps) ps->SetColor(color->GetColorPS(RED));
      else pen->SetColor(color->GetColor(RED));
      }

    sprintf(buffer, "%.1f%% %.1f%%",
	(float)stats.tBarElapsedtime / stats.DASelapsedTime * 100, olap);
    }

  if (ps) { ps->MoveTo(950, 750-(y+50)); ps->ShowStr(buffer); }
  else pen->DrawText(Surface(), 950, y+50, buffer);
  if (ps) ps->SetColor(color->GetColorPS(BLACK));
  else pen->SetColor(color->GetColor(BLACK));


{
  int nRows, nCols, colWidth;
  float		res2;

nCols = 5;
colWidth = Width() / nCols;

  res2 = (float)stats.resolution * stats.resolution / 1000000;

  switch (displayMode)
    {
    case ENCHILADA:
    case NORMAL:
      sprintf(buffer,
	"sv: act = %.2lfL, used = %.3lfL, area = %.2fmm2, conc = %.3lfN/L, lw = %.3lfg/M3, z = %.3lfdb",
	stats.SampleVolume / 1000, stats.DOFsampleVolume / 1000,
	res2 * stats.area, stats.concentration, stats.lwc, stats.dbz);

      if (ps) { ps->MoveTo(315, 750-(y+62)); ps->ShowStr(buffer); }
      else pen->DrawText(Surface(), 315, y+62, buffer);

      for (i = 0; cp = (Particle *)stats.particles.DeQueue(); ++i);
//printf("Normal: %d unremoved particles\n", i);
      break;

    case DIAGNOSTIC:
      sprintf(buffer, "freq = %f,  mean=%u min=%u max=%u",
	stats.frequency * 1000, stats.meanBar, stats.minBar, stats.maxBar);

      if (ps) { ps->MoveTo(505, 750-(y+62)); ps->ShowStr(buffer); }
      else pen->DrawText(Surface(), 505, y+62, buffer);

      for (i = 0; cp = (Particle *)stats.particles.DeQueue(); ++i);
//printf("Diagnostic: %d unremoved particles\n", i);
      break;
    }

}

exit:
  p = (ulong *)record->data;
  prevSlice[0] = p[1022];
  prevSlice[1] = p[1023];
  prevOverLoad = record->overld;
  prevTime = thisTime;

  y += PIX_PER_Y;

}       /* END DRAW */
 
/* -------------------------------------------------------------------- */
void MainCanvas::enchiladaLineItem(PostScript *ps, int i, int cnt,
	Particle *cp)
{
  int	h, m, s;

  if (ps) ps->SetColor(color->GetColorPS(BLACK));
  else pen->SetColor(color->GetColor(BLACK));

  if (cnt == 0)	// Print title.
    {
    strcpy(buffer, " #     Time       timeWord  rj  iy  ix  ia    dt   live");

    if (ps) {
       ps->MoveTo(5, 750); ps->ShowStr(buffer); }
    else
       pen->DrawText(Surface(), 5, 120, buffer);
    }


  h = cp->time / 3600;
  m = (cp->time - (h*3600)) / 60;
  s = cp->time - (h*3600) - (m*60);

  // Particle #, time stamp, timeword, reject, h, w, a
  sprintf(buffer, "%03d %02d:%02d:%02d.%03d  %8d %2d %3d %3d %3d %6d %6d",
	cnt, h, m, s, cp->msec, cp->timeWord, cp->reject, cp->h, cp->w,
	cp->area, cp->deltaTime, cp->liveTime);

  if (ps) {
    ps->MoveTo(5, 750-(y+80+(cnt*15))); ps->ShowStr(buffer); }
  else
    pen->DrawText(Surface(), 5, 137+(cnt*15), buffer);

}

/* -------------------------------------------------------------------- */
void MainCanvas::drawSlice(PostScript *ps, int i, ulong slice)
{
  int		j, cnt;
  XPoint	pts[32];

  if (slice == 0xffffffff)
    return;

  if (ps)
    {
    int       first;

    ps->MoveTo(i+37, 750-y-32);

    if (slice == 0x00000000)
      ps->rLineTo(0, 32);
    else
    if (slice != 0xffffffff)
      for (cnt = j = 0; j < 32; )
        {
        cnt = 1;
        first = (slice >> j) & 0x00000001;

        while (((slice >> ++j) & 0x00000001) == first && j < 32)
          ++cnt;

        if (first)
          ps->rMoveTo(0, cnt);
        else
          ps->rLineTo(0, cnt);
        }
    }
  else
    {
    for (cnt = j = 0; j < 32; ++j)
      if ( !((slice >> j) & 0x00000001) )
        {
        pts[cnt].x = i + 12;
        pts[cnt].y = y + (31-j);
        ++cnt;
        }

    pen->DrawPoints(Surface(), pts, cnt);
    }

}

/* END MAINCANVAS.CC */
