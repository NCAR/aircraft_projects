/*
-------------------------------------------------------------------------
OBJECT NAME:	getmem.c

FULL NAME:	Get Memory

ENTRY POINTS:	GetMemory()

STATIC FNS:	none

DESCRIPTION:	malloc data space, report error and exit if necassary

INPUT:		unsigned	nbytes_to_malloc

OUTPUT:		char *

REFERENCES:	malloc

COPYRIGHT:	University Corporation for Atmospheric Research, 1992
-------------------------------------------------------------------------
*/

#include <stdio.h>
#include <stdlib.h>


/* -------------------------------------------------------------------- */
void *GetMemory(size_t nbytes)
{
  char	*p;

  if ((p = malloc(nbytes)) == NULL)
    {
    fprintf(stderr, "Memory allocation failure, exiting.\n");
    exit(1);
    }

  return(p);

}	/* END GETMEMORY */

/* END GETMEM.C */
