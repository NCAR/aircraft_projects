/*
-------------------------------------------------------------------------
OBJECT NAME:	Titles.h

FULL NAME:	View Variable Titles

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef TITLES_H
#define TITLES_H

#include "define.h"

#include "TextWindow.h"
#include "DataFile.h"


/* -------------------------------------------------------------------- */
class Titles : public TextWindow {

public:

	Titles(const Widget parent);
  void	Update(const std::string fileName);

private:

};	/* END TITLES.H */

#endif
