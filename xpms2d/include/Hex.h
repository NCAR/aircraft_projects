/*
-------------------------------------------------------------------------
OBJECT NAME:	Hex.h

FULL NAME:	View Hex

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2000
-------------------------------------------------------------------------
*/

#ifndef HEX_H
#define HEX_H

#include "define.h"
#include "header.h"

#include "TextWindow.h"


/* -------------------------------------------------------------------- */
class Hex : public TextWindow {

public:

	Hex(const Widget parent);

  void	Update(int nBuffs, P2d_rec sets[]);

private:

};	/* END HEX.H */

#endif
