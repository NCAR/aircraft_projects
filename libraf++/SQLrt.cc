/*
-------------------------------------------------------------------------
OBJECT NAME:	SQLrt.cc

FULL NAME:	Real-time SQl data retriever.

TYPE:		Concrete

ENTRY POINTS:	

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 2003
-------------------------------------------------------------------------
*/

#include "SQLrt.h"


/* -------------------------------------------------------------------- */
SQLrt::SQLrt()
{
  /* make a connection to the database, use "setenv" environment
   * variables for connection info.
   */
  conn = PQconnectdb("");

  /* check to see that the backend connection was successfully made
   */
  if (PQstatus(conn) == CONNECTION_BAD)
  {
    fprintf(stderr, "Connection to database failed, check environment variables PGHOST, PGDATABASE & PGUSER.\n");
    fprintf(stderr, "%s", PQerrorMessage(conn));
    PQfinish(conn);
    conn = NULL;
  }
                                                                                
  sprintf(sqlBuff, "LISTEN current");
  res = PQexec(conn, sqlBuff);
  PQerrorMessage(conn);

  PQclear(res);

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
int SQLrt::GetVariable(const char vn[], char start[], char end[], float buff[])
{
  int	cnt = 0;




  return(cnt);

}	/* END GETVARIABLE */

/* -------------------------------------------------------------------- */
int SQLrt::GetSince(const char vn[], char last[], float buff[])
{
  int	cnt = 0;



  return(cnt);

}	/* END GETSINCE */

/* END SQLRT.CC */
