/*
-------------------------------------------------------------------------
OBJECT NAME:	Enchilada.h

FULL NAME:	View Enchilada

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2000
-------------------------------------------------------------------------
*/

#ifndef ENCHILADA_H
#define ENCHILADA_H

#include "define.h"

#include "TextWindow.h"


/* -------------------------------------------------------------------- */
class Enchilada : public TextWindow {

public:

	Enchilada(const Widget parent);

  void	AddLineItem(int cnt, Particle *cp);

private:

};	/* END ENCHILADA.H */

#endif
