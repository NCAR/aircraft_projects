/*
-------------------------------------------------------------------------
OBJECT NAME:	DataFile.h

FULL NAME:	Data File Class

ENTRY POINTS:	

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef DATAFILE_H
#define DATAFILE_H

#ifdef PNG
#include <zlib.h>
#endif

#include "define.h"

#include "Probe.h"
#include "hdrAPI.h"

/* ADS image record types */
#define ADS_WORD	0x4144
#define HDR_WORD	0x5448
#define SDI_WORD	0x8681
#define AVAPS_WORD	0x4156

#define PMS2DC1		0x4331
#define PMS2DC2		0x4332
#define PMS2DG1		0x4731
#define PMS2DG2		0x4732
#define PMS2DH1		0x4831
#define PMS2DH2		0x4832
#define PMS2DP1		0x5031
#define PMS2DP2		0x5032
 
#define PMS2_SIZE	4116
#define PMS2_RECSIZE	(0x8000 / PMS2_SIZE) * PMS2_SIZE


/* -------------------------------------------------------------------- */
class ADS_DataFile {

public:
  ADS_DataFile(char fName[]);
  ~ADS_DataFile();

  char	*FileName()	 { return(fileName); }
  char	*ProjectNumber() { return(hdr ? hdr->ProjectNumber() : (char *)""); }
  char	*FlightNumber()	 { return(hdr ? hdr->FlightNumber() : (char *)""); }
  char	*FlightDate()	 { return(hdr ? hdr->FlightDate() : (char *)""); }
  char	*HeaderVersion() { return(hdr ? hdr->Version() : (char *)""); }

  int	NumberOfProbes()	{ return(nProbes); }
  void	SetPosition(int position);
  int	GetPosition()	{ return(100 * currPhys / nIndices); }

//  int	NextSyncRecord(char buff[]);
  bool	LocatePMS2dRecord(P2d_rec *buff, int h, int m, int s);
  bool	FirstPMS2dRecord(P2d_rec *buff);
  bool	NextPMS2dRecord(P2d_rec *buff);
  bool	PrevPMS2dRecord(P2d_rec *buff);

  int	NextPhysicalRecord(char buff[]);

  void	ToggleSyntheticData();

  Probe	*probe[MAX_PROBES];

private:
  typedef struct { long index; short time[3]; } Index;

  void		buildIndices(), sort_the_table(int, int), SortIndices(int);
  void		SwapPMS2D(P2d_rec *);

  char		fileName[PATH_LEN];
  Header	*hdr;
#ifdef PNG
  gzFile	gz_fd;
#else
  int		gz_fd;
#endif
  FILE		*fp;
  long		savePos;

  int		nProbes;
  bool		diskData, gzipped, hasRAFheader, useTestRecord;

  Index		*indices;
  long		currPhys;
  int		currLR, nIndices;

  P2d_rec	physRecord[P2DLRPR], *testRecP;

};	/* END DATAFILE.H */

#endif
