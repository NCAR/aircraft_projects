/*
-------------------------------------------------------------------------
OBJECT NAME:	XmQuery.h

FULL NAME:	Motif Query Dialog

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef XMQUERY_H
#define XMQUERY_H

#include <Xm/Xm.h>
#include <Xm/MessageB.h>
#include <Xm/SelectioB.h>
#include <Xm/Text.h>


/* -------------------------------------------------------------------- */
class XmQuery {

public:
	XmQuery(Widget parent);
  void	QueryUser(char str[], int maxlen, void (*callBack)());
  void	ExtractAnswer(char *s);

private:
  Widget	queryBox;

};	/* END XMQUERY.H */

#endif
