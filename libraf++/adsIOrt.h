/*
-------------------------------------------------------------------------
OBJECT NAME:	adsIOrt.h

FULL NAME:	Class for reading real-time ADS images.

ENTRY POINTS:	

DESCRIPTION:	This class will allow forward scanning of ADS files.

COPYRIGHT:	University Corporation for Atmospheric Research, 1999
-------------------------------------------------------------------------
*/

#ifndef ADSIORT_H
#define ADSIORT_H

#include <cstdio>
#include <cstring>
#include <cstdlib>

#include "hdrAPI.h"

/* ADS image physical record types */
#define ADS_WORD	0x4144
#define HDR_WORD	0x5448
#define SDI_WORD	0x8681
#define AVAPS_WORD	0x4156
#define MCR_WORD	0x4d43
#define MASP_WORD	0x4450

#define PMS2DC1		0x4331
#define PMS2DC2		0x4332
#define PMS2DG1		0x4731
#define PMS2DG2		0x4732
#define PMS2DH1		0x4831
#define PMS2DH2		0x4832
#define PMS2DP1		0x5031
#define PMS2DP2		0x5032
 
#define PMS2_SIZE	sizeof(P2d_rec)
#define PMS2_LRPPR	(0x8000 / PMS2_SIZE)
#define PMS2_RECSIZE	((0x8000 / PMS2_SIZE) * PMS2_SIZE)


/* -------------------------------------------------------------------- */
class ADS_rtFile {

public:
	ADS_rtFile();
	~ADS_rtFile();

  Header	*hdr;


  bool	FirstSyncRecord(char buff[]);
  bool	NextSyncRecord(char buff[]);
  bool	LastSyncRecord(char buff[], int minusN);
  bool	LastSyncRecord(char buff[])	{ return(LastSyncRecord(buff, 0)); }

  bool	FirstMCRRecord(Mcr_rec *buff);
  bool	NextMCRRecord(Mcr_rec *buff);
  bool	LastMCRRecord(Mcr_rec *buff);

  bool	FirstPMS2dRecord(P2d_rec *buff);
  bool	NextPMS2dRecord(P2d_rec *buff);
  bool	LastPMS2dRecord(P2d_rec *buff, int minusN);
  bool	LastPMS2dRecord(P2d_rec *buff)	{ return(LastPMS2dRecord(buff, 1)); }

  bool	FirstGreyRecord(char buff[]);
  bool	NextGreyRecord(char buff[]);
  bool	LastGreyRecord(char buff[]);

  bool	FirstAvapsRecord(char buff[]);
  bool	NextAvapsRecord(char buff[]);
  bool	LastAvapsRecord(char buff[]);

  int	HdrBlkToSeconds(Hdr_blk *r)
    { return((ntohs(r->hour)%24)*3600 + ntohs(r->minute)*60 +ntohs(r->second));}

  int	HdrBlkToSeconds(P2d_rec r)
    { return((ntohs(r.hour)%24)*3600 + ntohs(r.minute)*60 +ntohs(r.second)); }

  int	HdrBlkToSeconds(P2d_rec *r)
    { return((ntohs(r->hour)%24)*3600 + ntohs(r->minute)*60 +ntohs(r->second));}

  int	HdrBlkToSeconds(GreyParticle r)
    { return((ntohs(r.hour)%24)*3600 + ntohs(r.minute)*60 +ntohs(r.second)); }

  int	HdrBlkToSeconds(GreyParticle *r)
    { return((ntohs(r->hour)%24)*3600 + ntohs(r->minute)*60 +ntohs(r->second));}

  int	HdrBlkToSeconds(Mcr_rec r)
    { return((ntohs(r.hour)%24)*3600 + ntohs(r.minute)*60 +ntohs(r.second)); }

  int	HdrBlkToSeconds(Mcr_rec *r)
    { return((ntohs(r->hour)%24)*3600 + ntohs(r->minute)*60 +ntohs(r->second));}

  int fileLengthSync()
	{ return(!fstat(fileno(fpSync), &fileInfo) ? fileInfo.st_size : -1); }

  int fileLength2D()
	{ return(!fstat(fileno(fp2D), &fileInfo) ? fileInfo.st_size : -1); }

  int fileLengthGrey()
	{ return(!fstat(fileno(fpGrey), &fileInfo) ? fileInfo.st_size : -1); }

  int fileLengthMCR()
	{ return(!fstat(fileno(fpMCR), &fileInfo) ? fileInfo.st_size : -1); }

  int fileLengthAVAPS()
	{ return(!fstat(fileno(fpAVAPS), &fileInfo) ? fileInfo.st_size : -1); }


private:
  FILE	*fpSync, *fp2D, *fpGrey, *fpMCR, *fpAVAPS;

  struct stat   fileInfo;
  time_t	lastMod;

  void	readFileName(), checkFileName();
  void	openFiles(), closeFiles(), resetFiles();
  int	NextPhysicalRecord(char buff[], FILE *fp, int lrLen);

  int	headOffset;

  char	*projDir;
  char	fileBaseName[256], rtFileFileName[256];
  char	physRecord[MX_PHYS];

};	/* END ADSIORT.H */

#endif
