/*
-------------------------------------------------------------------------
OBJECT NAME:	PMSspex.cc

FULL NAME:	

ENTRY POINTS:	InitPMSspecs()
		GetParameter()
		GetList()

STATIC FNS:	none

DESCRIPTION:	

INPUT:		

OUTPUT:		

REFERENCES:	none

REFERENCED BY:	User level applications (xbuild, WINDS).

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1995
-------------------------------------------------------------------------
*/

#include <cctype>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <iostream>

#include "PMSspex.h"

using namespace std;

/* -------------------------------------------------------------------- */
PMSspex::PMSspex(char fileName[])
{
  int	i, cnt;
  char	*file[2048], PMSbuffer[512], *p;
  FILE	*fp;

  if ((fp = fopen(fileName, "r")) == NULL)
    {
    cerr << "PMSspex: Can't open " << fileName << ".\n";
    exit(1);
    }


  /* Read file and strip out comments.
   */
  for (cnt = 0; fgets(PMSbuffer, 512, fp); )
    {
    if (PMSbuffer[0] == COMMENT)
      continue;

    PMSbuffer[strlen(PMSbuffer)] = '\0';	/* Ditch newline	*/

    if ( (p = strchr(PMSbuffer, COMMENT)) )
      *p = '\0';
    else
      p = &PMSbuffer[strlen(PMSbuffer)];

    while ( isspace(*(--p)) )	/* Strip trailing white-space	*/
      *p = '\0';

    if ( isspace(PMSbuffer[0]) )	/* Belongs to previous line	*/
      {
      char *p1;

      p1 = new char [strlen(file[cnt-1]) + strlen(PMSbuffer)+1];
      strcpy(p1, file[cnt-1]);
      strcat(p1, PMSbuffer);
      delete [] file[cnt-1];
      file[cnt-1] = p1;
      }
    else	/* Fresh line		*/
      {
      file[cnt] = new char [strlen(PMSbuffer)+1];
      strcpy(file[cnt], PMSbuffer);
      ++cnt;
      }
    }

  fclose(fp);


  PMSfile = new char *[cnt+1];

  for (i = 0; i < cnt; ++i)
    PMSfile[i] = file[i];

  PMSfile[i] = NULL;

}	/* END INITPMSSPECS */

/* -------------------------------------------------------------------- */
char *PMSspex::GetParameter(char serialNumber[],  char parameter[])
{
  int	i;
  char	*p;

  for (i = 0; PMSfile[i]; ++i)
    {
    if (strncmp(PMSfile[i], "START", 5) == 0)
      {
      for (p = &PMSfile[i][5]; *p == ' ' || *p == '\t'; ++p)
        ;

      if (strcmp(serialNumber, p) == 0)
        {
        int	len = strlen(parameter);

        for (; PMSfile[i]; ++i)
          {
          if (strcmp(PMSfile[i], "END") == 0)
            return(NULL);

          if (strncmp(PMSfile[i], parameter, len) == 0)
            {
            if (PMSfile[i][len] != ' ' && PMSfile[i][len] != '\t')
              continue;

            for (p = &PMSfile[i][len]; *p == ' ' || *p == '\t'; ++p)
              ;

            return(p);
            }
          }
        }
      }
    }

  return(NULL);

}	/* END GETPMSPARAMETER */

/* -------------------------------------------------------------------- */
PMSspex::~PMSspex()
{
  if (PMSfile)
    {
    int	i;

    for (i = 0; PMSfile[i]; ++i)
      free(PMSfile[i]);

    delete [] PMSfile;
    }

}	/* END RELEASEPMSSPECS */

/* -------------------------------------------------------------------- */
int PMSspex::GetSerialNumList(char *list[]) /* returns list of serial numbers */
{
  int     i, len, cnt = 0;
  char    *p;

  list[0] = NULL;

  for (i = 0; PMSfile[i]; ++i)
    if (strncmp(PMSfile[i], "START", 5) == 0)
      {
      for (p = &PMSfile[i][5]; *p == ' ' || *p == '\t'; ++p)
        ;

      list[cnt] = new char [len];
      strcpy(list[cnt], p);
      list[++cnt] = NULL;
      }

  return(cnt);

}	/* END GETPMSLIST */

/* END INIT.C */
