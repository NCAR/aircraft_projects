/*
-------------------------------------------------------------------------
OBJECT NAME:	PMSspex.h

DESCRIPTION:	Header file for PMSspec's files.

COPYRIGHT:	University Corporation for Atmospheric Research, 1998
-------------------------------------------------------------------------
*/

#ifndef PMSSPEX_H
#define PMSSPEX_H

#ifndef NULL
#define NULL		(0)
#endif

#define COMMENT		'#'


/* -------------------------------------------------------------------- */
class PMSspex
{
public:
	PMSspex(char fName[]);
	~PMSspex();

  char 	*GetParameter(char serialNumber[],  char parameter[]);
  int 	GetSerialNumList(char *list[]);


private:
  char	**PMSfile;

};

#endif

/* END PMSSPEX.H */
