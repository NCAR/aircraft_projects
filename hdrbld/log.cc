/*
-------------------------------------------------------------------------
OBJECT NAME:	hdrbld.c

FULL NAME:

ENTRY POINTS:	AddToChangeLog()
		DiffSDI()
		DumpToChangeLog()

STATIC FNS:	none

DESCRIPTION:

INPUT:

OUTPUT:

REFERENCES:	Xwin.c, init.c then enters XtAppMainLoop()

REFERENCED BY:	user

COPYRIGHT:	University Corporation for Atmospheric Research, 2001
-------------------------------------------------------------------------
*/

#include "hdrbld.h"

#include <time.h>

static int	logCnt = 0;
static char	*changeLog[512];

/* -------------------------------------------------------------------- */
void AddToChangeLog(char newMsg[])
{
  changeLog[logCnt] = GetMemory(strlen(newMsg)+1);
  strcpy(changeLog[logCnt], newMsg);
  ++logCnt;

}

/* -------------------------------------------------------------------- */
void DiffSDI(Sh *old, Sh *new)
{
  int	i;
  char	temp[32];
  bool	CalsChanged = FALSE;


  if (strcmp(old->dsm_locn, new->dsm_locn))
    {
    sprintf(buffer, "\tDSM: from %s to %s\n", old->dsm_locn, new->dsm_locn);
    AddToChangeLog(buffer);
    }

  if (strcmp(old->type, new->type))
    {
    sprintf(buffer, "\tType: from %s to %s\n", old->type, new->type);
    AddToChangeLog(buffer);
    }

  if (old->rate != new->rate)
    {
    sprintf(buffer, "\tRate: from %ld to %ld\n", old->rate, new->rate);
    AddToChangeLog(buffer);
    }

  if (old->adsaddr != new->adsaddr)
    {
    sprintf(buffer, "\tAddress: from %ld to %ld\n", old->adsaddr, new->adsaddr);
    AddToChangeLog(buffer);
    }

  if (old->ch_gain != new->ch_gain)
    {
    sprintf(buffer, "\tGain: from %ld to %ld\n", old->ch_gain, new->ch_gain);
    AddToChangeLog(buffer);
    }

  if (old->ch_offset != new->ch_offset)
    {
    sprintf(buffer, "\tOffset: from %ld to %ld\n", old->ch_offset, new->ch_offset);
    AddToChangeLog(buffer);
    }

  if (old->order != new->order)
    {
    sprintf(buffer, "\tCals: from %ld to %ld\n", old->order, new->order);
    AddToChangeLog(buffer);
    CalsChanged = TRUE;
    }
  else
    for (i = 0; i < old->order; ++i)
      if (old->cof[i] != new->cof[i])
        CalsChanged = TRUE;

  if (CalsChanged)
    {
    strcpy(buffer, "\tOld Cals: ");
    for (i = 0; i < old->order; ++i)
      {
      sprintf(temp, "%f ", old->cof[i]);
      strcat(buffer, temp);
      }

    AddToChangeLog(buffer);

    strcpy(buffer, "\tNew Cals: ");
    for (i = 0; i < new->order; ++i)
      {
      sprintf(temp, "%f ", new->cof[i]);
      strcat(buffer, temp);
      }

    AddToChangeLog(buffer);
    }

}	/* END DIFFSDI */

/* -------------------------------------------------------------------- */
void DumpToChangeLog(char FileName[])
{
  FILE		*fp;
  int		i;
  char		*slash;
  time_t	t;

  strcpy(buffer, FileName);
  slash = strrchr(buffer, '/');

  if (slash == NULL)
    buffer[0] = '\0';
  else
    slash[1] = '\0';

  strcat(buffer, "HeaderChangeLog");


  if ((fp = fopen(buffer, "a")) == NULL)
    {
    fprintf(stderr, "Can't open %s.\n", FileName);
    return;
    }

  t = time(NULL);
  fprintf(fp, "\n%s\n", ctime(&t));

  for (i = 0; i < logCnt; ++i)
    fprintf(fp, changeLog[i]);

  fclose(fp);

}	/* END DUMPTOCHANGELOG */

/* END LOG.C */
