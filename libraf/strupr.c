/*
-------------------------------------------------------------------------
OBJECT NAME:	strupr.c

FULL NAME:	String Upper

ENTRY POINTS:	strupr()
		strlower()

DESCRIPTION:	Converts string to upper|lower case.

INPUT:		Char pointer

OUTPUT:		Returns argument

REFERENCES:	none
-------------------------------------------------------------------------
*/

#include <ctype.h>

/* -------------------------------------------------------------------- */
char *strupr(char s[])
{
  char	*p;

  for (p = s; *p; ++p)
    *p = toupper(*p);

  return(s);

}	/* END STRUPR */

/* -------------------------------------------------------------------- */
char *strlower(char s[])
{
  char	*p;

  for (p = s; *p; ++p)
    *p = tolower(*p);

  return(s);

}	/* END STRLOWER */

/* END STRUPR.C */
