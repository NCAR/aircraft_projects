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
  char  *destHost, *p, script[512];

  p = getenv("ADS");
  strcpy(script, p);
  strcat(script, "/disc/scripts/");
  strcat(script, (char *)client);

  if (fork() == 0)
    {
    execlp("xterm", "xterm", opts[0], opts[1], opts[2], opts[3], opts[4],
                        opts[5], opts[6], script, buffer, NULL);

    printf("exec of xterm failed (script %s), errno = %d\n", script, errno);
    }

}       /* END FORKXTERM4XFER */

/* END FXTERM.C */
