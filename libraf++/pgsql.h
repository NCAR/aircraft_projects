/*
-------------------------------------------------------------------------
OBJECT NAME:	adsIOrt.h

FULL NAME:	Class for reading real-time ADS images.

ENTRY POINTS:	

DESCRIPTION:	This class will allow forward scanning of ADS files.

COPYRIGHT:	University Corporation for Atmospheric Research, 1999
-------------------------------------------------------------------------
*/

#ifndef SQLRT_H
#define SQLRT_H

#include <cstdio>
#include <cstring>
#include <cstdlib>

#include <libpq-fe.h>

/* -------------------------------------------------------------------- */
class SQLrt {

public:
	SQLrt();

  bool	GetVariableFirst(char buff[]);
  bool	GetVariableNext(char buff[]);
  bool	GetVariableLatest(char buff[], int minusN);
  bool	GetVariableLatest(char buff[])	{ return(GetVariableLatest(buff, 0)); }


private:
  PGconn        *conn;
  PGresult      *res;
  PGnotify      *rc;

  char	sqlBuff[8192];


};	/* END SQLRT.H */

#endif
