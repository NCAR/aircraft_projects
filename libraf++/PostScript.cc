/*
-------------------------------------------------------------------------
OBJECT NAME:	PostScript.cc

FULL NAME:	PostScript Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "PostScript.h"

#include <pwd.h>
#include <time.h>
#include <sys/types.h>
#include <unistd.h>

using namespace std;

extern Printer	*printerSetup;
void		ErrorMsg(char msg[]);


/* -------------------------------------------------------------------- */
PostScript::PostScript(char *outFile, char progName[], const string& title, float scale)
{
  if (outFile)
    {
    if ((fp = fopen(outFile, "w")) == NULL)
      {
      char buff[256];

      sprintf(buff, "PostScript: Can't open output file %s", outFile);
      ErrorMsg(buff);
      return;
      }

    file = True;
    }
  else
    {
    if ((fp = popen(printerSetup->lpCommand(), "w")) == NULL)
      {
      ErrorMsg("PostScript: can't open pipe to 'lp'.");
      return;
      }

    file = False;
    }

  PSheader(progName, title, scale);

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void PostScript::PSheader(char progName[], const string& title, float scale)
{
  char		*user, *date;
  time_t        printTime = time((time_t *)NULL);

  user = (getpwuid(getuid()))->pw_gecos;
  date = ctime(&printTime);
 
  /* Print standard header info, and convert to 100 dpi.
   */
  fprintf(fp, "%%!PS-Adobe-3.0 EPSF-3.0\n");
  fprintf(fp, "%%%%Creator: %s\n", progName);
  fprintf(fp, "%%%%For: %s\n", (getpwuid(getuid()))->pw_gecos);
  fprintf(fp, "%%%%Title: %s\n", title.c_str());
  fprintf(fp, "%%%%CreationDate: %s", ctime(&printTime));
  fprintf(fp, "%%%%Pages: 1\n");
  fprintf(fp, "%%%%BoundingBox: 0 0 %d %d\n",
                     (int)(612 * printerSetup->WidthRatio()),
                     (int)(792 * printerSetup->HeightRatio()));
  fprintf(fp, "%%%%Orientation: %s\n",
      printerSetup->Shape() == Printer::PORTRAIT ? "Portrait" : "Landscape");
  fprintf(fp, "%%%%DocumentNeededResources: font Times-Roman\n");
  fprintf(fp, "%%%%EndComments\n");
 
  fprintf(fp, "%%%%BeginDefaults\n");
  fprintf(fp, "%%%%PageResources: font Times-Roman\n");
  fprintf(fp, "%%%%EndDefaults\n");
 
  fprintf(fp, "%%%%BeginProlog\n");
  fprintf(fp, "/rm /rmoveto load def\n");
  fprintf(fp, "/rl /rlineto load def\n");
  fprintf(fp, "/m /moveto load def\n");
  fprintf(fp, "/l /lineto load def\n");
  fprintf(fp, "/s /show load def\n");
  fprintf(fp, "/rs {dup stringwidth pop 120 exch sub 0 rmoveto show");
  fprintf(fp, "} bind def\n");
  fprintf(fp, "%%%%EndProlog\n");
 
  fprintf(fp, "%%%%BeginSetup\n");
  fprintf(fp, "%%%%IncludeResource: font Times-Roman\n");
  fprintf(fp, "save\n");

  fprintf(fp, "%g %g scale\n", scale, scale);
  fprintf(fp, "%%%%EndSetup\n");
 
  fprintf(fp, "%%%%Page: 1 1\n");

  if (printerSetup->Shape() == Printer::LANDSCAPE)
    {
    fprintf(fp, "%d %d translate\n", 0, (int)(792 / scale));
    fprintf(fp, "-90 rotate\n");

    MoveTo((int)(712 / scale), (int)(587 / scale));
    }
  else
    {
    MoveTo((int)(500 / scale), (int)(762 / scale));
    }

  fprintf(fp, "/Times-Roman findfont\n");
  fprintf(fp, "dup length dict begin\n");
  fprintf(fp, " {1 index /FID ne {def} {pop pop} ifelse } forall\n");
  fprintf(fp, " /Encoding ISOLatin1Encoding def\n");
  fprintf(fp, " currentdict\n");
  fprintf(fp, "end\n");
  fprintf(fp, "/Times-Roman-ISOLatin1 exch definefont pop\n");

  fprintf(fp, "/Times-Roman findfont %d scalefont setfont\n", (int)(5 / scale));
  fprintf(fp, "(%s, %s) show\n", user, date);

}	/* END PSHEADER */

/* -------------------------------------------------------------------- */
void PostScript::SetFont(int size)
{
  fprintf(fp, "/Times-Roman-ISOLatin1 findfont %d scalefont setfont\n",
		(int)(printerSetup->FontRatio() * size));

}	/* END SETFONT */

/* -------------------------------------------------------------------- */
void PostScript::SetClipping(int vd, int hd)
{
  fprintf(fp, "gsave\n");
  fprintf(fp, "0 0 moveto\n");
  fprintf(fp, "%d 0 rlineto\n", hd);
  fprintf(fp, "0 %d rlineto\n", vd);
  fprintf(fp, "%d neg 0 rlineto\n", hd);
  fprintf(fp, "closepath\n");
  fprintf(fp, "clip\n");
  fprintf(fp, "newpath\n");

}       /* END SETCLIP */

/* -------------------------------------------------------------------- */
void PostScript::ClearClipping()
{
  fprintf(fp, "stroke\n");
  fprintf(fp, "grestore\n");
  fprintf(fp, "newpath\n");

}       /* END CLEARCLIP */

/* -------------------------------------------------------------------- */
void PostScript::DrawBox(int lv, int th, int rv, int bh)
{
  /* Draw the bounding box for graph.
   */
  fprintf(fp, "3 setlinewidth\n");
  fprintf(fp, "stroke\n");
  MoveTo(lv, th);
  LineTo(rv, th);
  LineTo(rv, bh);
  LineTo(lv, bh);
  LineTo(lv, th);
  fprintf(fp, "stroke\n");

}	/* END DRAWBOX */

/* -------------------------------------------------------------------- */
PostScript::~PostScript()
{
  fprintf(fp, "stroke\n");
  fprintf(fp, "showpage\n");
  fprintf(fp, "%%%%Trailer\n");
  fprintf(fp, "restore\n");
  fprintf(fp, "%%EOF\n");
 
  if (file)
    fclose(fp);
  else
    pclose(fp);

}	/* END DESTRUCTOR */

/* END POSTSCRIPT.CC */
