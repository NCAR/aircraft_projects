/*
-------------------------------------------------------------------------
OBJECT NAME:	PlotInfo.h

FULL NAME:	Plot Information

ENTRY POINTS:	

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef PLOTINFO_H
#define PLOTINFO_H

#include "define.h"


/* -------------------------------------------------------------------- */
class PlotInfo {

public:
	PlotInfo();
	~PlotInfo();

  char	*Title()	{ return(title); }
  char	*SubTitle()	{ return(subTitle); }

  void	GenerateDefaultTitles();


private:
  char	title[TITLESIZE], subTitle[TITLESIZE];


};	/* END PLOTINFO.H */

#endif
