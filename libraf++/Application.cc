/*
-------------------------------------------------------------------------
OBJECT NAME:	Application.cc

FULL NAME:	

ENTRY POINTS:	

STATIC FNS:	

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-8
-------------------------------------------------------------------------
*/

#include "Application.h"


/* -------------------------------------------------------------------- */
Application::Application(const char APP_CLASS[], int *argc, char *argv[],
	String fallback_resources[])
{
  shell = XtAppInitialize(&context, APP_CLASS, NULL, 0, argc, argv,
                          fallback_resources, NULL, 0);
 
}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void Application::FlushEvents()
{
  while (XtAppPending(context))
    XtAppProcessEvent(context, XtIMAll);

}	/* END FLUSHEVENTS */

/* -------------------------------------------------------------------- */
Application::~Application()
{
  XtDestroyWidget(shell);

}	/* END DESTRUCTOR */

/* END APPLICATION.CC */
