/*
-------------------------------------------------------------------------
OBJECT NAME:	FileMgr.h

FULL NAME:	Data File Manager

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef FILEMGR_H
#define FILEMGR_H

#include "define.h"

#include "DataFile.h"
#include "PlotMgr.h"


/* -------------------------------------------------------------------- */
class FileManager {

public:
	FileManager();

  friend class DataSource;

  void		NewFile(char fileName[]);
  void		AddFile(char fileName[]);

  void		SetCurrentFile(int newFile)	{ currentFile = newFile; }

  int		NumberOfFiles()	const	{ return(numberFiles); }
  DataFile	*CurrentFile() const
	{ return(numberFiles == 0 ? (DataFile *)NULL : dataFile[currentFile]); }

  DataFile	*FirstFile()
	{ return(numberFiles == 0 ? (DataFile *)NULL : dataFile[nextCnt = 0]); }

  DataFile	*NextFile()
	{ return(++nextCnt == numberFiles ? (DataFile *)NULL : dataFile[nextCnt]); }


private:
  int	numberFiles;
  int	currentFile;
  int	nextCnt;

  DataFile	*dataFile[MAX_DATAFILES];

};	/* END FILEMGR.H */

#endif
