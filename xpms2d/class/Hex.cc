/*
-------------------------------------------------------------------------
OBJECT NAME:	Hex.cc

FULL NAME:	

ENTRY POINTS:	Update()

STATIC FNS:	

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2000
-------------------------------------------------------------------------
*/

#include "Hex.h"

/* -------------------------------------------------------------------- */
Hex::Hex(const Widget parent) : TextWindow(parent, "hex")
{

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void Hex::Update(int nBuffs, P2d_rec sets[])
{
  int	i, j;

  Clear();

  /* Title */
  strcpy(buffer, "      ");
  for (j = 0; j < nBuffs; ++j)
    sprintf(&buffer[strlen(buffer)], "   %s    ", (char *)&sets[j].id);

  strcat(buffer, "\n");
  Append(buffer);


  /* Records */
  for (i = 0; i < 1024; ++i)
    {
    sprintf(buffer, "%4d  ", i);

    for (j = 0; j < nBuffs; ++j)
      sprintf(&buffer[strlen(buffer)], "%08X ", *(long *)(&sets[j].data[i<<2]));

    strcat(buffer, "\n");
    Append(buffer);
    }

  MoveTo(0);

}	/* END UPDATE */

/* END HEX.CC */
