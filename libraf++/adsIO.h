/*
-------------------------------------------------------------------------
OBJECT NAME:	adsIO.h

FULL NAME:	Class for reading ADS images.

ENTRY POINTS:	

DESCRIPTION:	This class will allow forward scanning of ADS files.

COPYRIGHT:	University Corporation for Atmospheric Research, 1998
-------------------------------------------------------------------------
*/

#ifndef ADSIO_H
#define ADSIO_H

#include <cstdio>
#include <cstring>

#include "tapeIO.h"
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
class ADS_DataFile {

public:
	ADS_DataFile(char fName[]);
	~ADS_DataFile();

  Header	*hdr;


  int	NextPhysicalRecord(char buff[]);

  bool	FirstSyncRecord(char buff[]);
  bool	NextSyncRecord(char buff[]);

  bool	FirstMCRRecord(Mcr_rec *buff);
  bool	NextMCRRecord(Mcr_rec *buff);

  bool	FirstPMS2dRecord(P2d_rec *buff);
  bool	NextPMS2dRecord(P2d_rec *buff);

  int	HdrBlkToSeconds(Hdr_blk *r)
    { return((ntohs(r->hour)%24)*3600 + ntohs(r->minute)*60 +ntohs(r->second));}

  int	HdrBlkToSeconds(P2d_rec r)
    { return((ntohs(r.hour)%24)*3600 + ntohs(r.minute)*60 +ntohs(r.second)); }

  int	HdrBlkToSeconds(P2d_rec *r)
    { return((ntohs(r->hour)%24)*3600 + ntohs(r->minute)*60 +ntohs(r->second));}

  int	HdrBlkToSeconds(Mcr_rec r)
    { return((ntohs(r.hour)%24)*3600 + ntohs(r.minute)*60 +ntohs(r.second)); }

  int	HdrBlkToSeconds(Mcr_rec *r)
    { return((ntohs(r->hour)%24)*3600 + ntohs(r->minute)*60 +ntohs(r->second));}


  // These are supplied more for development and debugging use.
  long	filePos()	{ return(ftell(fp)); }
  void	setPos(long x)	{ fseek(fp, x, SEEK_SET); }


private:
  FILE	*fp;

  bool		diskData;
  TapeDrive	*tape;

  void	resetFile();
  int	curr2dLR, currSyncLR;

  char	physRecord[MX_PHYS];
  char	*syncPhysRecord, *twoDPhysRecord;

};	/* END ADSIO.H */

#endif
