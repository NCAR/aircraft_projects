/*
-------------------------------------------------------------------------
OBJECT NAME:	adsIO.cc

FULL NAME:	ADS Data File Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1998
-------------------------------------------------------------------------
*/

#include "adsIO.h"

#include <unistd.h>
#include <iostream>

/* -------------------------------------------------------------------- */
ADS_DataFile::ADS_DataFile(char fName[])
{
  int	Ccnt, Pcnt;

  Ccnt = Pcnt = 0;
  diskData = strncmp(fName, "/dev", 4) ? true : false;

  if (diskData)
    {
    if ((fp = fopen(fName, "rb")) == NULL)
      std::cerr << "adsIO: Can't open input file " << fName << ".\n";
    else
      hdr = new Header(fName);
    }
  else
    {
    fp = (FILE *)(-1);
    tape = new TapeDrive(fName);
    hdr = new Header(*tape);
    tape->Seek(0);
    }

  currSyncLR = curr2dLR = 1000;

  syncPhysRecord = twoDPhysRecord = NULL;

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
bool ADS_DataFile::FirstSyncRecord(char buff[])
{
  resetFile();
  return(NextSyncRecord(buff));

}	/* END FIRSTSYNCRECORD */

/* -------------------------------------------------------------------- */
bool ADS_DataFile::NextSyncRecord(char buff[])
{
  if (fp == NULL)
    return(false);

  if (syncPhysRecord == NULL)
    syncPhysRecord = new char [hdr->lrLength() * hdr->lrPpr()];

  if (++currSyncLR >= hdr->lrPpr())
    {
    do
      {
      if (NextPhysicalRecord(physRecord) <= 0)
        return(false);
      }
    while (ntohs(((ushort *)physRecord)[0]) != SDI_WORD);
 
    memcpy(syncPhysRecord, physRecord, hdr->lrLength() * hdr->lrPpr());
    currSyncLR = 0;
    }

  memcpy((void *)buff, (void *)&syncPhysRecord[currSyncLR * hdr->lrLength()],
		hdr->lrLength());
  return(true);

}	/* END NEXTSYNCRECORD */

/* -------------------------------------------------------------------- */
bool ADS_DataFile::FirstMCRRecord(Mcr_rec *buff)
{
  resetFile();
  return(NextMCRRecord(buff));

}	/* END FIRSTMCRRECORD */

/* -------------------------------------------------------------------- */
bool ADS_DataFile::NextMCRRecord(Mcr_rec *buff)
{
  if (fp == NULL)
    return(false);

  do
    {
    if (NextPhysicalRecord(physRecord) <= 0)
      return(false);
    }
  while (strncmp(physRecord, "MCR-", 4));

  memcpy((void *)buff, physRecord, sizeof(Mcr_rec));
  return(true);

}	/* END NEXTMCRRECORD */

/* -------------------------------------------------------------------- */
bool ADS_DataFile::FirstPMS2dRecord(P2d_rec *buff)
{
  resetFile();
  return(NextPMS2dRecord(buff));

}	/* END FIRSTPMS2DRECORD */

/* -------------------------------------------------------------------- */
bool ADS_DataFile::NextPMS2dRecord(P2d_rec *buff)
{
  bool done = false;

  if (fp == NULL)
    return(false);

  if (twoDPhysRecord == NULL)
    twoDPhysRecord = new char [PMS2_RECSIZE];

  if (++curr2dLR >= PMS2_LRPPR)
    {
    do
      {
      if (NextPhysicalRecord(physRecord) <= 0)
        return(false);

      if (physRecord[1] == '1' || physRecord[1] == '2')
        {
        char	c = physRecord[0];

        if (c == 'C' || c == 'P' || c == 'H' || c == 'G')
          done = true;
        }
      }
    while (!done);
 
    memcpy((void *)twoDPhysRecord, (void *)physRecord, PMS2_SIZE * PMS2_LRPPR);
    curr2dLR = 0;
    }

  memcpy((void *)buff, (void *)&twoDPhysRecord[curr2dLR*PMS2_SIZE], PMS2_SIZE);
 
  return(true);

}	/* END NEXTPMS2DRECORD */

/* -------------------------------------------------------------------- */
int ADS_DataFile::NextPhysicalRecord(char buff[])
{
  int	rc, idWord;
  int	size = sizeof(short);

  if (diskData == FALSE)
    size = tape->Read(buff);
  else
    {
    rc = fread(buff, size, 1, fp);

    if (rc != 1)
      return(0);

    idWord = ntohs(*((ushort *)buff));

    switch (idWord)
      {
      case SDI_WORD:
        size = (hdr->lrLength() * hdr->lrPpr()) - sizeof(short);
        break;

      case ADS_WORD:
        size = 18;
        break;

      case HDR_WORD:
        size = hdr->HeaderLength() - sizeof(short);
        break;

      case PMS2DC1: case PMS2DC2:	// PMS 2D
      case PMS2DP1: case PMS2DP2:
      case PMS2DH1: case PMS2DH2:	// HVPS
        size = PMS2_RECSIZE - sizeof(short);
        break;

      case 0x4d43:	// MCR
        size = sizeof(Mcr_rec) - sizeof(short);
        break;

      case PMS2DG1: case PMS2DG2:	// GrayScale
        size = 32000 - sizeof(short);
        break;

      default:
        size = 0;
      }

    if (fread(&buff[sizeof(short)], size, 1, fp) != 1)
      size = 0;

    size += sizeof(short);
    }

  return(size);

}	/* END NEXTPHYSICALRECORD */

/* -------------------------------------------------------------------- */
ADS_DataFile::~ADS_DataFile()
{
  if (fp == NULL)
    return;

  if (diskData)
    fclose(fp);
  else
    delete tape;

  if (syncPhysRecord)
    delete [] syncPhysRecord;

  if (twoDPhysRecord)
    delete [] twoDPhysRecord;

}	/* END DESTRUCTOR */

/* -------------------------------------------------------------------- */
void ADS_DataFile::resetFile()
{
  if (fp == NULL)
    return;

  currSyncLR = curr2dLR = 1000;

  if (diskData)
    rewind(fp);
  else
    tape->Seek(3);

}	/* END RESETFILE */

/* END ADSIO.CC */
