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


/* -------------------------------------------------------------------- */
FileManager::FileManager()
{
  numberFiles = 0;
  currentFile = 0;

}	/* END CONTRUCTOR */

/* -------------------------------------------------------------------- */
void FileManager::NewFile(char fileName[])
{
  extern PlotManager	*plotMgr;

  while (--numberFiles >= 0)
    delete dataFile[numberFiles];

  numberFiles = 1;
  currentFile = 0;

  dataFile[0] = new DataFile(fileName);

  plotMgr->GenerateAutoTitles(*dataFile[0]);

}	/* END NEWFILE */

/* -------------------------------------------------------------------- */
void FileManager::AddFile(char fileName[])
{
  dataFile[numberFiles++] = new DataFile(fileName);

}	/* END ADDFILE */

/* END FILEMGR.CC */
