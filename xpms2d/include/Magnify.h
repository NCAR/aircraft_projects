/*
-------------------------------------------------------------------------
OBJECT NAME:	Magnify.h

FULL NAME:	Magnify window and Zoom

ENTRY POINTS:	

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef MAGNIFY_H
#define MAGNIFY_H

#include "define.h"


/* -------------------------------------------------------------------- */
class Magnify {

public:
	Magnify();

  void  DrawBox(XMotionEvent *evt);
  void  ProcessInput(XmDrawingAreaCallbackStruct *evt);

  int	startX, startY;
  int	endX, endY;
  int	width, height;


private:
  void  RemoveBox();

};	/* END MAGNIFY.H */

#endif
