/*
-------------------------------------------------------------------------
OBJECT NAME:	XmFile.h

FULL NAME:	Motif File Selection Box

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef XMFILE_H
#define XMFILE_H

#include <Xm/Xm.h>
#include <Xm/FileSB.h>


/* -------------------------------------------------------------------- */
class XmFile {

public:
	XmFile(Widget parent);
  void	QueryFile(char prompt[], char dir[], XtCallbackProc callBack);
  void	ExtractFileName(XmString str, char **text);

private:
  Widget	fileBox;

};	/* END XMFILE.H */

#endif
