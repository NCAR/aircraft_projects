/*
-------------------------------------------------------------------------
OBJECT NAME:	Header.cc

FULL NAME:	

ENTRY POINTS:	Update()

STATIC FNS:	

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-8
-------------------------------------------------------------------------
*/

#include "Header.h"


/* -------------------------------------------------------------------- */
Header::Header(const Widget parent) : TextWindow(parent, "header")
{

}

/* -------------------------------------------------------------------- */
void Header::Update(const std::string fileName)
{
  FILE	*pp;

  Clear();
  Append(fileName.c_str());
  Append("\n\n");
 
  sprintf(buffer, "ncdump -h %s", fileName.c_str());
  if ((pp = popen(buffer, "r")) == NULL)
    {
    sprintf(buffer, "Can't open pipe [%s]", buffer);
    ErrorMsg(buffer);
    }
 
  while (fread(buffer, BUFFSIZE, 1, pp) > 0)
    Append(buffer);
 
  strcpy(strchr(buffer, '}')+1, "\n\n");
  Append(buffer);
 
  pclose(pp);

  MoveTo(0);

}	/* END UPDATE */

/* END HEADER.CC */
