/*
-------------------------------------------------------------------------
OBJECT NAME:	tapeIO.c

FULL NAME:	Tape IO procedures.

ENTRY POINTS:	TapeAssign(int fd)
		TapeClose()
		TapeOpen(char *FileName)
		TapeRead(char *Buffer)
		TapeSeek(long RecordNumber)
		TapeStat(struct mtget *)
		TapeTell()

DESCRIPTION:	man tapeIO

		TapeOpen() opens a tape drive as read only.  The file
		descriptor is maintained internally along with the
		current record number.

		TapeAssign() assigns a fd to the internal fd.  This is
		useful if you already have a device opened and don't
		want to reopen it.

		TapeRead() reads the next physical record.  Upon reaching
		end of file it returns 0.  Since the last positions the
		tape head into the next file, TapeRead() will back up to
		ensure you have not advanced to the next file.

		TapeTell() returns the Current Physical Record Number.
INPUT:		

OUTPUT:		ERR/OK

REFERENCES:	open, read, close, ioctl

REFERENCED BY:	none

COPYRIGHT:	University Corporation for Atmospheric Research, 1992
-------------------------------------------------------------------------
*/

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/uio.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/mtio.h>

#ifndef ERR
#define OK	(0)
#define ERR	(-1)
#endif

#ifndef RECORDSIZE
#define RECORDSIZE	(0x8000)
#endif

static int	tape_fd;
static int	CurrentPR;	/* Current Physical Record Number	*/


/* -------------------------------------------------------------------- */
TapeAssign(int fd)
{
	struct mtget	stat;

	tape_fd = fd;
	TapeStat(&stat);
	CurrentPR = stat.mt_blkno;

	return(OK);

}	/* END TAPEASSIGN */

/* -------------------------------------------------------------------- */
TapeOpen(char name[])
{
	if ((tape_fd = open(name, O_RDONLY)) == ERR)
		{
		fprintf(stderr, "TapeOpen: can't open %s\n", name);
		TapeStat(NULL);
		return(ERR);
		}

	TapeSeek(0L);

	return(OK);

}	/* END TAPEOPEN */

/* -------------------------------------------------------------------- */
TapeRead(char *record)
{
	int	rc;
	struct mtget	stat1, stat2;

	TapeStat(&stat1);

	if ((rc = read(tape_fd, record, RECORDSIZE)) == ERR)
		{
		fprintf(stderr, "TapeRead: read error, errno=%d\n", errno);
		TapeStat(NULL);
		return(ERR);
		}

	if (rc == 0)
		{
		TapeStat(&stat2);

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

}	/* END TAPEREAD */

/* -------------------------------------------------------------------- */
TapeSeek(long start_rec)
{
	struct mtop	tape_op;

	/* Some attempted optimization.  Assuming Rewind is faster than seeks.
	 * If the distance to the new rec is less than the distance from BOT
	 * to new rec, then rewind tape first.
	 */
	if (start_rec == 0 || (start_rec+5) < CurrentPR / 2)
		{
		printf("Rewinding tape\n"); fflush(stdout);

		tape_op.mt_op   = MTREW;
		tape_op.mt_count= 1;

		if (ioctl(tape_fd, MTIOCTOP, &tape_op) == ERR)
			{
			fprintf(stderr, "TapeSeek: rewind failed\n");
			TapeStat(NULL);
			return(ERR);
			}

		tape_op.mt_count = start_rec;
		}
	else
		tape_op.mt_count = start_rec - CurrentPR;

	if (start_rec != 0)
		{
		printf("Skipping %d records\n",tape_op.mt_count);fflush(stdout);
		tape_op.mt_op	= MTFSR;

		if (ioctl(tape_fd, MTIOCTOP, &tape_op) == ERR)
			{
			fprintf(stderr, "TapeSeek: seek failed\n");
			TapeStat(NULL);
			return(ERR);
			}
		}

	CurrentPR = start_rec;
TapeStat(NULL);
	return(CurrentPR);

}	/* END TAPESEEK */

/* -------------------------------------------------------------------- */
TapeClose()
{
	close(tape_fd);
	return(OK);

}	/* END TAPECLOSE */

/* -------------------------------------------------------------------- */
TapeTell()
{
	return(CurrentPR);

}	/* END TAPETELL */

/* -------------------------------------------------------------------- */
TapeStat(struct mtget *their_stat)
{
	int		rc;
	struct mtget	stat;

	if ((rc = ioctl(tape_fd, MTIOCGET, &stat)) == ERR)
		{
		fprintf(stderr, "TapeStat: ioctl failed\n");
		return(ERR);
		}


	if (their_stat)
		memcpy(their_stat, &stat, sizeof(struct mtget));
	else
		{
		printf("TapeStat: CurrentPR=%d, ", CurrentPR);
		printf("ioctl=%d, dsreg=%d, erreg=%d, fileno=%d, blkno=%d\n",
		rc, stat.mt_dsreg,stat.mt_erreg, stat.mt_fileno,stat.mt_blkno);
		}

	return(OK);

}	/* END TAPESTAT */

/* END TAPEIO.C */
