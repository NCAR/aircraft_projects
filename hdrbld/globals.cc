/*
-------------------------------------------------------------------------
OBJECT NAME:	globals.c

FULL NAME:	Global Variable Definitions

ENTRY POINTS:	none

DESCRIPTION:	

COPYRIGHT:	University Corporation for Atmospheric Research, 1996
-------------------------------------------------------------------------
*/

#include "hdrbld.h"

char	buffer[8192];		/* Generic, volatile string space	*/
char	*ProjectDirectory, *ProjectNumber, ProjectName[64];
char	FileName[512], *DSM[MAX_DSM];

char	*aircraft[8];

Sh	*sdi[MX_SDI];		/* SDI (aka raw) variable list		*/
Sh	currentSh;
Fl	flightInfo;
int	nsdi, nPMS;


int	Inertial[2], GPS[3];

bool	ChangesMade;

/* END GLOBALS.C */
