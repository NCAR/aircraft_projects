/*
-------------------------------------------------------------------------
OBJECT NAME:	MagnifyCanvas.h

FULL NAME:	Magnify canvas

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef MAGCANVAS_H
#define MAGCANVAS_H

#include "define.h"
#include "header.h"

#include "Canvas.h"


/* -------------------------------------------------------------------- */
class MagnifyCanvas : public Canvas {

public:
		MagnifyCanvas(Widget w);

  void          draw();


private:

};	/* END MAGNIFYCANVAS.H */

#endif
