/*
-------------------------------------------------------------------------
OBJECT NAME:	PostageWindow.h

FULL NAME:	Create Postage Window

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef POSTWIN_H
#define POSTWIN_H

#include "define.h"

#include "Time.h"
#include "Window.h"

#include <Xm/Form.h>
#include <Xm/Frame.h>
#include <Xm/Label.h>
#include <Xm/PushB.h>
#include <Xm/RowColumn.h>
#include <Xm/Scale.h>
#include <Xm/TextF.h>

/* -------------------------------------------------------------------- */
class PostageWindow : public WinForm {

public:
		PostageWindow(Widget parent);
  void		PopUp();

  int		AveragePeriod();

  void		SetCurrentTime();
  int		IncrementCurrentTime();

  void		PageForward();
  void		PageBackward();


private:
  Widget	timeText[2], averageText;

  FlightClock	start, end;
  int		currSecond, numberSeconds;

  void		createXwindow(Widget parent);

};	/* END POSTAGEWINDOW.H */

#endif
