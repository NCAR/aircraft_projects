/*
-------------------------------------------------------------------------
OBJECT NAME:	fork.c

FULL NAME:	Callback for forking various processes

ENTRY POINTS:	HeaderDump()
		EditVarDB()
		forkXterm()
		forkXterm4xfer()

STATIC FNS:	none

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	

COPYRIGHT:	University Corporation for Atmospheric Research, 1996-2001
-------------------------------------------------------------------------
*/

#include "hdrbld.h"
#include "ac.h"

#include <sys/types.h>
#include <errno.h>
#include <stdlib.h>
#include <unistd.h>

static char *opts[] = {
		"-g",
		"=80x20+500+350",
		"-T",
		"hdrbld script",
		"-e",
		"rsh",
		"mistral" };


/* -------------------------------------------------------------------- */
void HeaderDump(Widget w, XtPointer client, XtPointer call)
{
  if (ProjectDirectory == NULL || ProjectNumber == NULL)
    return;

  if (fork() == 0)
    {
    execlp("xhd", "xhd", ProjectNumber, NULL);
    fprintf(stderr, "hdrbld: failed to fork xhd.\n");
    exit(1);
    }

}	/* END HEADERDUMP */

/* -------------------------------------------------------------------- */
void EditVarDB(Widget w, XtPointer client, XtPointer call)
{
  if (ProjectDirectory == NULL || ProjectNumber == NULL)
    return;

  sprintf(buffer, "%s/%s/VarDB", ProjectDirectory, ProjectNumber);

  if (fork() == 0)
    {
    execlp("vared", "vared", buffer, NULL);
    fprintf(stderr, "hdrbld: failed to fork vared.\n");
    exit(1);
    }

}	/* END EDITVARDB */

/* -------------------------------------------------------------------- */
void forkXterm4xfer(Widget w, XtPointer client, XtPointer call)
{
  char	*destHost, *p, script[512];

  p = getenv("ADS");
  strcpy(script, p);
  strcat(script, "/disc/scripts/");
  strcat(script, (char *)client);

  destHost = GetAircraftParameter(flightInfo.acraft, "NFS_SERVER");

  if (destHost == NULL)
    {
    sprintf(buffer, "NFS_SERVER not defined for aircraft %s\n", flightInfo.acraft);

    ShowError(buffer);
    return;
    }


  if (fork() == 0)
    {
    execlp("xterm", "xterm", opts[0], opts[1], opts[2], opts[3], opts[4],
			opts[5], opts[6], script, destHost, NULL);

    printf("exec of xterm failed (script %s), errno = %d\n", script, errno);
    }

}	/* END FORKXTERM4XFER */

/* -------------------------------------------------------------------- */
void forkXterm(Widget w, XtPointer client, XtPointer call)
{
  char  *p, script[512];

  if (ProjectNumber == NULL)
    {
    ShowError("No Project Number.");
    return;
    }

  p = getenv("ADS");
  strcpy(script, p);
  strcat(script, "/disc/scripts/");
  strcat(script, (char *)client);

  if (fork() == 0)
    {
    execlp("xterm", "xterm", opts[0], opts[1], opts[2], opts[3], opts[4],
                        opts[5], opts[6], script, ProjectNumber, NULL);

    printf("exec of xterm failed (script %s), errno = %d\n", script, errno);
    }

}       /* END FORKXTERM */

/* END FORK.C */
