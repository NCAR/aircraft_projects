/*
-------------------------------------------------------------------------
OBJECT NAME:	FileMgr.cc

FULL NAME:	File Manager Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "FileMgr.h"

extern ADS_DataFile	*dataFile[];


/* -------------------------------------------------------------------- */
FileManager::FileManager()
{
  numberFiles = 0;
  currentFile = 0;

}	/* END CONTRUCTOR */

/* -------------------------------------------------------------------- */
void FileManager::NewFile(char fileName[])
{
  int	i;

  for (i = numberFiles-1; i >= 0; --i)
    delete dataFile[i];

  numberFiles = 1;
  currentFile = 0;

  dataFile[0] = new ADS_DataFile(fileName);

}	/* END NEWFILE */

/* -------------------------------------------------------------------- */
void FileManager::AddFile(char fileName[])
{
  dataFile[numberFiles++] = new ADS_DataFile(fileName);

}	/* END ADDFILE */

/* END FILEMGR.CC */
