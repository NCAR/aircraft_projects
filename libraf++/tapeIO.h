/*
-------------------------------------------------------------------------
OBJECT NAME:	tapeIO.h

FULL NAME:	Tape IO class

ENTRY POINTS:	

DESCRIPTION:	

COPYRIGHT:	University Corporation for Atmospheric Research, 1998
-------------------------------------------------------------------------
*/

#ifndef TAPEDRIVE_H
#define TAPEDRIVE_H

#include <sys/types.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/mtio.h>

#define RECORDSIZE	65535

#ifndef ERR
#define ERR		(-1)
#endif

#ifndef OK
#define OK		0
#endif

/* -------------------------------------------------------------------- */
class TapeDrive
{
public:
	TapeDrive(const char fileName[]);
	TapeDrive(int fd);	// Assign open file descriptor
	~TapeDrive();

  int	Stat(struct mtget *);
  long	Seek(long recNum);
  int	Read(char record[]);
  void	Close();

private:
  int	tape_fd;
  long	CurrentPR;

};

#endif
