/*
-------------------------------------------------------------------------
OBJECT NAME:	SQLrt.h

FULL NAME:	Class for reading SQL database (PostGreS).

ENTRY POINTS:	

DESCRIPTION:	

COPYRIGHT:	University Corporation for Atmospheric Research, 2003
-------------------------------------------------------------------------
*/

#ifndef SQLRT_H
#define SQLRT_H

#include <libpq-fe.h>

#include <cstdio>
#include <cstring>


/* -------------------------------------------------------------------- */
class SQLrt {

public:
	SQLrt();
	~SQLrt();

  GetVariable(const char vn[], char st[], char et[], float buff[]);
  GetSince(const char vn[], char last[], float buff[]);


private:
  PGconn	*conn;
  PGresult	*res;
  PGnotify	*rc;


};	/* END SQLRT.H */

#endif
