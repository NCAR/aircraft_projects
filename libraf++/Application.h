/*
-------------------------------------------------------------------------
OBJECT NAME:	Application.h

FULL NAME:	Create X application

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-8
-------------------------------------------------------------------------
*/

#ifndef APPLICATION_H
#define APPLICATION_H

#include <X11/Intrinsic.h>
#include <X11/StringDefs.h>


/* -------------------------------------------------------------------- */
class Application {

public:
		Application(const char APP_CLASS[], int *argc, char *argv[],
			String fallback_resources[]);
		~Application();

  Widget	Shell() const	{ return(shell); }
  XtAppContext	Context() const	{ return(context); }

  void		FlushEvents();


private:
  Widget	shell;
  XtAppContext	context;


};	/* END APPLICATION.H */

#endif
