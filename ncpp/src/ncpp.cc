/*
-------------------------------------------------------------------------
OBJECT NAME:	ncpp.cc

FULL NAME:	nc Particle Probe

ENTRY POINTS:	main()
		ErrorMsg()

STATIC FNS:	Initialize()
		ProcessArgs()
		ReadConfigFile()

DESCRIPTION:	See man page.

NOTES:		This is/was my first C++ program, please be kind.

AUTHOR:		websterc@ncar.ucar.edu

COPYRIGHT:      University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include <new.h>
#include <unistd.h>

#include "define.h"
#include "fbr.h"

#include "Application.h"
#include "Canvas.h"
#include "CanvasWindow.h"
#include "Cursor.h"
#include "FileMgr.h"
#include "MovieControl.h"
#include "PlotMgr.h"
#include "Printer.h"
#include "SetMgr.h"
#include "XmError.h"
#include "XmFile.h"

Application	*application;
Canvas		*mainCanvas;
PlotManager	*plotMgr;
MovieControl	*movieControlGUI;
XCursor		cursor;
Printer		*printerSetup;

SetManager	setMgr;
FileManager	fileMgr;

XmFile		*fileSel;

void		outOfMemory();

static void  Initialize();
static void  ProcessArgs(char *argv[]), ReadConfigFile();
void SetColorNames(char str[]);


/* --------------------------------------------------------------------- */
int main(int argc, char *argv[])
{
  set_new_handler(outOfMemory);

  ncopts = 0;
  Initialize();

  application = new Application("XmNCpp", &argc, argv, fallback_resources);

  CanvasWindow	canvasWindow(application->Shell());
  canvasWindow.PopUp();

  mainCanvas = new Canvas(canvasWindow.DrawingArea());


  movieControlGUI = new MovieControl(application->Shell());
  movieControlGUI->PopUp();
  setMgr.SetNumberRecords(1);

  printerSetup	= new Printer(application->Shell());
  fileSel	= new XmFile(application->Shell());

  plotMgr = new PlotManager(application->Shell(), canvasWindow.DrawingArea());
  plotMgr->PopUp();

  SetPlotTypeCB(NULL, XY, NULL);
  ModifyActiveDataTypes(NULL, NULL, NULL);

  ReadConfigFile();

  ProcessArgs(argv);

  XtAppMainLoop(application->Context());

  return(0);

}	/* END MAIN */

/* --------------------------------------------------------------------- */
static void Initialize()
{
  char	*p;

  if ((p = (char *)getenv("DATA_DIR")) != NULL)
    {
    strcpy(DataPath, p);
    strcat(DataPath, "/*.nc");
    }
  else
    strcpy(DataPath, "/*");

  p = (char *)getenv("HOME");
  strcpy(UserPath, p);
  strcat(UserPath, "/nimbus/*");

}	/* END INITIALIZE */

/* --------------------------------------------------------------------- */
static void ProcessArgs(char **argv)
{
  while (*++argv)
    if ((*argv)[0] == '-')
      switch ((*argv)[1])
        {
        }
    else
      {
      if (access(*argv, R_OK) == 0)
        NewDataFile(NULL, (XtPointer)*argv, NULL);
      }

}	/* END PROCESSARGS */

/* --------------------------------------------------------------------- */
static void ReadConfigFile()
{
  FILE  *fp;
  char  *p;

  if ((p = getenv("HOME")) == NULL)
    return;

  sprintf(buffer, "%s/.ncplotrc", p);

  if ((fp = fopen(buffer, "r")) == NULL)
    return;

  while (fgets(buffer, 1024, fp) > 0)
    {
    if (buffer[0] == '#' || strlen(buffer) < 3)
      continue;

    p = strchr(buffer, '=') + 1;

    if (p == (char *)1)
       continue;

    while (isspace(*p))
      ++p;

    p[strlen(p)-1] = '\0'; /* ditch newline */

    if (strncmp(buffer, "Colors", 6) == 0)
      {
      SetColorNames(p);
      }
    else
    if (strncmp(buffer, "PrintCommand", 12) == 0)
      {
      printerSetup->SetCommand(p);
      }
    else
    if (strncmp(buffer, "PrintColor", 10) == 0)
      {
      if (strncmp(p, "Color", 5) == 0)
        printerSetup->SetColor(true);
      }
    else
    if (strncmp(buffer, "LineWidth", 9) == 0)
      {
      if (atoi(p) > 1)
        {
        plotMgr->SetLineWidth(atoi(p));
        printerSetup->SetLineWidth(atoi(p)<<1);
        }
      }

    }

}       /* END READCONFIGFILE */

/* --------------------------------------------------------------------- */
void ErrorMsg(char msg[])
{
  new XmError(application->Shell(), msg);

}	/* END ERRORMSG */

/* --------------------------------------------------------------------- */
void outOfMemory()
{
  fprintf(stderr, "Out of memory, fatal.\n");
  exit(1);

}	/* END OUTOFMEMORY */

/* END NCPP.CC */
