/*
-------------------------------------------------------------------------
OBJECT NAME:	FileMgr.h

FULL NAME:	Data File Manager

ENTRY POINTS:	

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef FILEMGR_H
#define FILEMGR_H

#include "define.h"

#include "DataFile.h"


/* -------------------------------------------------------------------- */
class FileManager {

public:
	FileManager();

  void		NewFile(char fileName[]);
  void		AddFile(char fileName[]);

  void		SetCurrentFile(int newFile)	{ currentFile = newFile; }

  int		NumberOfFiles()		{ return(numberFiles); }
  ADS_DataFile	*CurrentFile()
		{ return(numberFiles == 0 ? (ADS_DataFile *)NULL : dataFile[currentFile]); }

  ADS_DataFile	*dataFile[MAX_DATAFILES];


private:
  int	numberFiles;
  int	currentFile;

};	/* END FILEMGR.H */

#endif
