/*
-------------------------------------------------------------------------
OBJECT NAME:	init.c

FULL NAME:	Initialize Global Variables

ENTRY POINTS:	Initialize()
		ProcessArgv()

STATIC FNS:		

DESCRIPTION:	

INPUT:		none

OUTPUT:		none

REFERENCES:	none

REFERENCED BY:	nimbus.c, cb_main.c

COPYRIGHT:	University Corporation for Atmospheric Research, 1996
-------------------------------------------------------------------------
*/

#include "hdrbld.h"
#include "ac.h"
#include "pms.h"
#include "vardb.h"


char	*getenv();


/* -------------------------------------------------------------------- */
void PreWidgetInitialize()
{
  char	*p;

  if ((ProjectDirectory = (char *)getenv("PROJ_DIR")) == NULL)
    {
    fprintf(stderr, "Environment variable PROJ_DIR not defined, this is fatal.\n");
    exit(1);
    }

  if (ProjectNumber)
    {
    FILE	*fp;

    sprintf(FileName, "%s/%s/header", ProjectDirectory, ProjectNumber);
    free(ProjectNumber);

    if ((fp = fopen(FileName, "rb")) == NULL)
      {
      fprintf(stderr, "Can't open %s.\n", FileName);
      ProjectNumber = NULL;
      }
    else
      {
      fread((char *)&flightInfo, sizeof(Fl), 1, fp);
      ProjectNumber = flightInfo.prnum;
      fclose(fp);
      }
    }

  nsdi = 0;
  sdi[0] = NULL;
  DSM[0] = NULL;
  Inertial[0] = Inertial[1] = 0;
  GPS[0] = GPS[1] = GPS[2] = 0;

  InitAircraftSpecs("AircraftSpecs");
  GetAircraftList(aircraft);


  if (ProjectNumber)
    {
    sprintf(buffer, "%s/%s/PMSspecs", ProjectDirectory, ProjectNumber);
    InitPMSspecs(buffer);
    sprintf(buffer, "%s/%s/VarDB", ProjectDirectory, ProjectNumber);
    InitializeVarDB(buffer);
    p = flightInfo.acraft;
    }
  else
    {
    sprintf(buffer, "%s/defaults/PMSspecs", ProjectDirectory);
    InitPMSspecs(buffer);
    sprintf(buffer, "%s/defaults/VarDB", ProjectDirectory);
    InitializeVarDB(buffer);
    p = aircraft[0];
    }

  SetDSMlist(p);

}

/* -------------------------------------------------------------------- */
void PostWidgetInitialize()
{
  ClearCurrentSh(NULL, NULL, NULL);

  if (ProjectNumber)
    OpenNewFile_OK(NULL, NULL, NULL);

}	/* END INITIALIZE */

/* -------------------------------------------------------------------- */
void ProcessArgv(int argc, char **argv)
{
  int		i;

  ProjectNumber = NULL;

  for (i = 1; i < argc; ++i)
    {
    if (argv[i][0] != '-')
      {
      ProjectNumber = GetMemory(strlen(argv[i]+1));
      strcpy(ProjectNumber, argv[i]);
      continue;
      }

    switch (argv[i][1])
      {
      default:
        fprintf(stderr, "Invalid option %s, ignoring.\n", argv[i]);
      }

    }

}	/* END PROCESSARGV */

/* END INIT.C */
