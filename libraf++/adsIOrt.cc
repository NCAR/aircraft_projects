/*
-------------------------------------------------------------------------
OBJECT NAME:	adsIOrt.cc

FULL NAME:	Real-time ADS Data File Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1999
-------------------------------------------------------------------------
*/

#include "adsIOrt.h"

#include <unistd.h>

/* -------------------------------------------------------------------- */
ADS_rtFile::ADS_rtFile()
{
  char	host[80], *p;

  if ((projDir = getenv("PROJ_DIR")) == NULL)
    {
    fprintf(stderr, "adsIOrt: PROJ_DIR undefined, fatal.\n");
    exit(1);
    }

  gethostname(host, 80);
  if ((p = strchr(host, '.')) ) *p = '\0';

  sprintf(rtFileFileName, "%s/hosts/%s/rtdata.filename", projDir, host);

  fpSync = fp2D = fpGrey = fpMCR = fpAVAPS = NULL;
  checkFileName();

  // Length of headers in each file.  Used to compute offsets.
  headOffset = 20 + (2 * hdr->HeaderLength());

}	/* END CONSTRUCTOR */
  
/* -------------------------------------------------------------------- */
bool ADS_rtFile::FirstSyncRecord(char buff[])
{
  checkFileName();

  if (fpSync)
    rewind(fpSync);

  return(NextSyncRecord(buff));

}	/* END FIRSTSYNCRECORD */

/* -------------------------------------------------------------------- */
bool ADS_rtFile::NextSyncRecord(char buff[])
{
  checkFileName();

  if (fpSync == NULL)
    return(false);

  do
    {
    if (NextPhysicalRecord(physRecord, fpSync, hdr->lrLength()) <= 0)
      return(false);
    }
  while (ntohs(((ushort *)physRecord)[0]) != SDI_WORD);
 
  memcpy((void *)buff, (void *)physRecord, hdr->lrLength());
  return(true);

}	/* END NEXTSYNCRECORD */

/* -------------------------------------------------------------------- */
bool ADS_rtFile::LastSyncRecord(char buff[], int minusN)
{
  checkFileName();

  if (fpSync == NULL)
    return(false);

  int nRecs = ((fileLengthSync() - headOffset) / hdr->lrLength()) - minusN;

  if (nRecs < 0)
    nRecs = 0;

  fseek(fpSync, headOffset + (nRecs * hdr->lrLength()), SEEK_SET);

  return(NextSyncRecord(buff));

}	/* END FIRSTSYNCRECORD */

/* -------------------------------------------------------------------- */
bool ADS_rtFile::FirstMCRRecord(Mcr_rec *buff)
{
  checkFileName();

  if (fpMCR)
    rewind(fpMCR);

  return(NextMCRRecord(buff));

}	/* END FIRSTMCRRECORD */

/* -------------------------------------------------------------------- */
bool ADS_rtFile::NextMCRRecord(Mcr_rec *buff)
{
  checkFileName();

  if (fpMCR == NULL)
    return(false);

  if (ftell(fpMCR) > 1009430000)
    {
    int		len;
    char	fileName[512];

    strcpy(fileName, fileBaseName);
    strcat(fileName, ".rawMCRm");
    fclose(fpMCR);

    len = strlen(fileName)-1;

    while ((fpMCR = fopen(fileName, "rb")) == NULL)
      --fileName[len];
    }

  do
    {
    if (NextPhysicalRecord(physRecord, fpMCR, sizeof(Mcr_rec)) <= 0)
      return(false);
    }
  while (strncmp(physRecord, "MCR-", 4));

  memcpy((void *)buff, (void *)physRecord, sizeof(Mcr_rec));
  return(true);

}	/* END NEXTMCRRECORD */

/* -------------------------------------------------------------------- */
bool ADS_rtFile::LastMCRRecord(Mcr_rec *buff)
{
  checkFileName();

  if (fpMCR == NULL)
    return(false);

  int nRecs = (fileLengthMCR() - headOffset) / sizeof(Mcr_rec);
  fseek(fpMCR, headOffset + (nRecs * sizeof(Mcr_rec)), SEEK_SET);

  return(NextMCRRecord(buff));

}	/* END LASTMCRRECORD */

/* -------------------------------------------------------------------- */
bool ADS_rtFile::FirstPMS2dRecord(P2d_rec *buff)
{
  checkFileName();

  if (fp2D)
    rewind(fp2D);

  return(NextPMS2dRecord(buff));

}	/* END FIRSTPMS2DRECORD */

/* -------------------------------------------------------------------- */
bool ADS_rtFile::NextPMS2dRecord(P2d_rec *buff)
{
  bool	done = false;
  int	size;

  checkFileName();

  if (fp2D == NULL)
    return(false);

  do
    {
    if ((size = NextPhysicalRecord(physRecord, fp2D, sizeof(P2d_rec))) <= 0)
      return(false);

    if (physRecord[1] == '1' || physRecord[1] == '2')
      {
      char	c = physRecord[0];

      if (c == 'C' || c == 'P' || c == 'H')
        done = true;
      }
    }
  while (!done);
 
  memcpy((void *)buff, (void *)physRecord, size);
 
  return(true);

}	/* END NEXTPMS2DRECORD */

/* -------------------------------------------------------------------- */
bool ADS_rtFile::LastPMS2dRecord(P2d_rec *buff, int minusN)
{
  checkFileName();

  if (fp2D == NULL)
    return(false);

  int nRecs = (fileLength2D() - headOffset) / sizeof(P2d_rec) - minusN;

  if (nRecs < 0)
    nRecs = 0;

  fseek(fp2D, headOffset + (nRecs * sizeof(P2d_rec)), SEEK_SET);
//fprintf(stderr, "adsIOrt.cc: %d %d\n", nRecs, ftell(fp2D));
  return(NextPMS2dRecord(buff));

}	/* END LASTPMS2DRECORD */

/* -------------------------------------------------------------------- */
bool ADS_rtFile::FirstGreyRecord(char buff[])
{
  checkFileName();

  if (fpGrey)
    rewind(fpGrey);

  return(NextGreyRecord(buff));

}	/* END FIRSTGREYRECORD */

/* -------------------------------------------------------------------- */
bool ADS_rtFile::NextGreyRecord(char buff[])
{
  bool	done = false;
  int	size;

  checkFileName();

  if (fpGrey == NULL)
    return(false);

  do
    {
    if ((size = NextPhysicalRecord(physRecord, fpGrey, sizeof(P2d_rec))) <= 0)
      return(false);

    if (physRecord[1] == '1' || physRecord[1] == '2')
      {
      char	c = physRecord[0];

      if (c == 'C' || c == 'P' || c == 'H' || c == 'G')
        done = true;
      }
    }
  while (!done);
 
  memcpy((void *)buff, (void *)physRecord, size);
 
  return(true);

}	/* END NEXTGREYRECORD */

/* -------------------------------------------------------------------- */
bool ADS_rtFile::LastGreyRecord(char buff[])
{
  checkFileName();

  if (fpGrey == NULL)
    return(false);

  // Greyscale has variable length records, so formulas don't work.
  int pos = fileLengthGrey() - 1024;	// Back off 1k.

  if (pos < headOffset)
    pos = headOffset;

  fseek(fpGrey, pos, SEEK_SET);

  return(NextGreyRecord(buff));

}	/* END LASTGREYRECORD */

/* -------------------------------------------------------------------- */
bool ADS_rtFile::FirstAvapsRecord(char *buff)
{
  checkFileName();

  if (fpAVAPS)
    rewind(fpAVAPS);

  return(NextAvapsRecord(buff));

}

/* -------------------------------------------------------------------- */
bool ADS_rtFile::NextAvapsRecord(char *buff)
{
  char	temp[1024];

  checkFileName();

  if (fpAVAPS == NULL)
    return(false);

  temp[0] = '\0';

  if (fgets(temp, 1024, fpAVAPS))
    {
    strcpy(buff, temp);
    return(true);
    }

  return(false);
}

/* -------------------------------------------------------------------- */
bool ADS_rtFile::LastAvapsRecord(char *buff)
{
  checkFileName();

  if (fpAVAPS)
    fseek(fpAVAPS, 0, SEEK_END);

  return(NextAvapsRecord(buff));
}


/* -------------------------------------------------------------------- */
int ADS_rtFile::NextPhysicalRecord(char buff[], FILE *fp, int lrLen)
{
  long	cp, ep;
  int	rc, idWord;
  int	size = sizeof(short);
  GreyParticle	gp;

  // Check for new data, if not enough has been written bail out.
  cp = ftell(fp);
  fseek(fp, 0, SEEK_END);
  ep = ftell(fp);
  fseek(fp, cp, SEEK_SET);

  if (ep - cp < lrLen)
    return(0);


  // Read, hopefully, ID word.
  rc = fread(buff, size, 1, fp);

  if (rc != 1)
    return(0);

  idWord = ntohs(*((ushort *)buff));

  switch (idWord)
    {
    case SDI_WORD:
      size = hdr->lrLength() - sizeof(short);
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
      size = sizeof(P2d_rec) - sizeof(short);
      break;

    case 0x4d43:	// MCR
      size = sizeof(Mcr_rec) - sizeof(short);
      break;

    case PMS2DG1: case PMS2DG2:	// GrayScale
      /* Because Greyscale physical records are variable length, we will treat
       * each particle as a record from disk based files.
       */
      size = sizeof(GreyParticle) - sizeof(short);
      break;

    default:
printf("NextPhysicalRecord: didn't land on a record, reading 2 more.\n");
printf(" byte = %d\n", idWord);
      size = 0;
    }

  if (fread(&buff[sizeof(short)], size, 1, fp) != 1)
    size = 0;

  if (idWord == PMS2DG1 || idWord == PMS2DG2)
    {
    size = ntohs(((GreyParticle *)buff)->slice_cnt) * 16;
    fread(&buff[sizeof(GreyParticle)], size, 1, fp);

    size += sizeof(GreyParticle);
    }
  else
    size += sizeof(short);

  return(size);

}	/* END NEXTPHYSICALRECORD */

/* -------------------------------------------------------------------- */
ADS_rtFile::~ADS_rtFile()
{
  closeFiles();

}	/* END DESTRUCTOR */

/* -------------------------------------------------------------------- */
void ADS_rtFile::readFileName()
{
  FILE	*fpNameFile;

  /* The real-time file name base is stored in the following file.
   * Read this name, so we know what files to open for sync, 2d, mcr, etc.
   */
  if ((fpNameFile = fopen(rtFileFileName, "r")) == NULL)
    {
    fprintf(stderr, "adsIOrt: Open of %s failed, fatal.\n", rtFileFileName);
    exit(1);
    }

  fgets(fileBaseName, 256, fpNameFile);
  fileBaseName[strlen(fileBaseName)-1] = '\0';
  fclose(fpNameFile);

}	/* END READFILENAME */

/* -------------------------------------------------------------------- */
void ADS_rtFile::checkFileName()
{
  stat(rtFileFileName, &fileInfo);

  if (fileInfo.st_mtime != lastMod)
    {
    fprintf(stderr, "adsIOrt: realtime data restarted, resetting files.\n");

    lastMod = fileInfo.st_mtime;
    readFileName();
    closeFiles();
    openFiles();
    resetFiles();
    }

}	/* END CHECKFILENAME */

/* -------------------------------------------------------------------- */
void ADS_rtFile::openFiles()
{
  char	fileName[256];

  strcpy(fileName, fileBaseName);
  strcat(fileName, ".ads");

  while ((fpSync = fopen(fileName, "rb")) == NULL)
    sleep(1);

  sleep(3);

  hdr = new Header(fileName);

  strcpy(fileName, fileBaseName);
  strcat(fileName, ".2d");
  fp2D = fopen(fileName, "rb");

  strcpy(fileName, fileBaseName);
  strcat(fileName, ".rawMCRa");
  fpMCR = fopen(fileName, "rb");

  strcpy(fileName, fileBaseName);
  strcat(fileName, ".Grey");
  fpGrey = fopen(fileName, "rb");

  strcpy(fileName, fileBaseName);
  strcat(fileName, ".avaps");
  fpAVAPS = fopen(fileName, "rb");

}	/* END OPENFILES */

/* -------------------------------------------------------------------- */
void ADS_rtFile::closeFiles()
{
  if (fpSync)
    fclose(fpSync);

  if (fp2D)
    fclose(fp2D);

  if (fpGrey)
    fclose(fpGrey);

  if (fpMCR)
    fclose(fpMCR);

  if (fpAVAPS)
    fclose(fpAVAPS);

  fpSync = fp2D = fpGrey = fpMCR = fpAVAPS = NULL;

}	/* END CLOSEFILES */

/* -------------------------------------------------------------------- */
void ADS_rtFile::resetFiles()
{
  if (fpSync)
    rewind(fpSync);

  if (fp2D)
    rewind(fp2D);

  if (fpGrey)
    rewind(fpGrey);

  if (fpMCR)
    rewind(fpMCR);

  if (fpAVAPS)
    rewind(fpAVAPS);

}	/* END RESETFILE */

/* END ADSIORT.CC */
