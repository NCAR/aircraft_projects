/*
-------------------------------------------------------------------------
OBJECT NAME:	tapeIO.cc

FULL NAME:	Tape IO procedures.

TYPE:		C++

ENTRY POINTS:	Seek(long RecordNumber)
		Read(char *Buffer)
		Stat()
		Close()

DESCRIPTION:	man tapeIO

INPUT:		

OUTPUT:		ERR/OK

REFERENCES:	open, read, close, ioctl

REFERENCED BY:	none
-------------------------------------------------------------------------
*/

#include "tapeIO.h"

#include <fcntl.h>
#include <unistd.h>
#include <iostream>

#include <cerrno>
#include <cstring>
#include <cstdio>

using namespace std;

/* -------------------------------------------------------------------- */
TapeDrive::TapeDrive(const char fileName[])
{
  struct mtget tstat;
  struct mtop op;

  if ((tape_fd = open(fileName, O_RDONLY)) == ERR)
    {
    cerr << "TapeDrive: can't open " << fileName << ", errno = " << errno << ".\n";
    Stat(NULL);
    }
  else
    {
    Seek(0L);
    CurrentPR = 0;
    }

#ifndef SVR4
  ioctl(tape_fd, MTIOCGET, &tstat);

  if (GMT_ONLINE(tstat.mt_gstat))
    {
    op.mt_op = MTSETBLK;
    op.mt_count = 0;
    ioctl(tape_fd, MTIOCTOP, &op);

    op.mt_op = MTSETDENSITY;
    op.mt_count = 0x15;
    ioctl(tape_fd, MTIOCTOP, &op);
    }

  close(tape_fd);
  tape_fd = ERR;
#endif

}	/* END OPEN */

/* -------------------------------------------------------------------- */
TapeDrive::TapeDrive(int fd)
{
  struct mtget	stat;

  tape_fd = fd;
  Stat(&stat);
  CurrentPR = stat.mt_blkno;

}	/* END ASSIGN */

/* -------------------------------------------------------------------- */
TapeDrive::~TapeDrive()
{
  Close();

}	/* END DESTRUCTOR */

/* -------------------------------------------------------------------- */
int TapeDrive::Read(char record[])
{
  int		rc;
  struct mtget	stat1, stat2;

  if (tape_fd == ERR)
    return(ERR);

  Stat(&stat1);

  if ((rc = read(tape_fd, record, RECORDSIZE)) == ERR)
    {
    cerr << "TapeRead: read error, errno = " << errno << ".\n";
    Stat(NULL);
    return(ERR);
    }

  if (rc == 0)
    {
    Stat(&stat2);

    if (stat2.mt_fileno == stat1.mt_fileno)
      {
      struct mtop	op;

      op.mt_op = MTBSF;	/* Skip back to prev file */
      op.mt_count = 1;
      ioctl(tape_fd, MTIOCTOP, &op);
      }
    }
  else
    ++CurrentPR;

  return(rc);

}	/* END READ */

/* -------------------------------------------------------------------- */
long TapeDrive::Seek(long start_rec)
{
  struct mtop	tape_op;

  if (tape_fd == ERR)
    return(ERR);

  /* Some attempted optimization.  Assuming Rewind is faster than seeks.
   * If the distance to the new rec is less than the distance from BOT
   * to new rec, then rewind tape first.
   */
  if (start_rec == 0 || (start_rec+5) < CurrentPR / 2)
    {
    cout << "Rewinding tape....";

    tape_op.mt_op   = MTREW;
    tape_op.mt_count= 1;

    if (ioctl(tape_fd, MTIOCTOP, &tape_op) == ERR)
      {
      cerr << " rewind failed.\n";
      Stat(NULL);
      return(ERR);
      }

    cout << "\n";
    tape_op.mt_count = start_rec;
    }
  else
    tape_op.mt_count = start_rec - CurrentPR;

  if (start_rec != 0)
    {
    cout << "Skipping " << tape_op.mt_count << " records.\n";
    tape_op.mt_op = MTFSR;

    if (ioctl(tape_fd, MTIOCTOP, &tape_op) == ERR)
      {
      cerr << "TapeSeek: seek failed.\n";
      Stat(NULL);
      return(ERR);
      }
    }

  CurrentPR = start_rec;
  Stat(NULL);

  return(CurrentPR);

}	/* END TAPESEEK */

/* -------------------------------------------------------------------- */
void TapeDrive::Close()
{
  if (tape_fd != ERR)
    {
    close(tape_fd);
    tape_fd = ERR;
    }

}	/* END CLOSE */

/* -------------------------------------------------------------------- */
int TapeDrive::Stat(struct mtget *their_stat)
{
  int		rc;
  struct mtget	stat;

  if (tape_fd == ERR)
    return(ERR);

  if ((rc = ioctl(tape_fd, MTIOCGET, &stat)) == ERR)
    {
    cerr << "TapeStat: ioctl failed.\n";
    return(ERR);
    }


  if (their_stat)
    memcpy(their_stat, &stat, sizeof(struct mtget));
  else
    {
    cout << "TapeStat: CurrentPR=" << CurrentPR;
    cout << ", ioctl=" << rc;
    cout << ", dsreg=" << stat.mt_dsreg;
    cout << ", erreg=" << stat.mt_erreg;
    cout << ", fileno=" << stat.mt_fileno;
    cout << ", blkno=" << stat.mt_blkno << ".\n";
    }

  return(OK);

}	/* END STAT */

/* END TAPEIO.CC */
