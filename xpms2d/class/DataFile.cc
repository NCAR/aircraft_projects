/*
-------------------------------------------------------------------------
OBJECT NAME:	DataFile.cc

FULL NAME:	ADS Data File Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-2001
-------------------------------------------------------------------------
*/

#include "DataFile.h"

#include <unistd.h>
#include <algorithm>

static P2d_rec PtestRecord, CtestRecord, HtestRecord;

static ulong PtestParticle[] = {
0xffffffff,
0xff000134,
0x55000000,

0xfffc3fff,
0xfff81fff,
0xfff00fff,
0xfff00fff,

0xfff00fff,
0xfff00fff,
0xfff81fff,
0xfffc3fff,

0xffffffff,
0xffffffff
 };

static ulong CtestParticle[] = {
0xffffffff,
0xff000e00,
0x55000000,

0xfff81fff,
0xffe007ff,
0xffc003ff,
0xff8001ff,
0xff8001ff,
0xff8001ff,
0xff0000ff,
0xff0000ff,

0xff0000ff,
0xff0000ff,
0xff8001ff,
0xff8001ff,
0xff8001ff,
0xffc003ff,
0xffe007ff,
0xfff81fff,

0xffffffff,
0xffffffff
 };

static ushort HtestParticle[] = {
0x8000,
0x807a,

0x427e,
0x437d,
0x447c,
0x447c,
0x447c,
0x447c,
0x437d,
0x427e,

 };


/* -------------------------------------------------------------------- */
ADS_DataFile::ADS_DataFile(char fName[])
{
  int	Ccnt, Pcnt, Hcnt;
  char	*name;
  void	*p;

  strcpy(fileName, fName);

  if (strstr(fileName, ".gz"))
    {
    gzipped = true;
    printf("We have gzipped file.\n");
    }
  else
    gzipped = false;

#ifdef PNG
  if (gzipped)
    gz_fd = gzopen(fileName, "rb");
  else
#endif
    fp = fopen(fileName, "rb");

  if ((gzipped && gz_fd <= 0) || (!gzipped && fp == NULL))
    {
    sprintf(buffer, "Can't open file %s", fileName);
    ErrorMsg(buffer);
    return;
    }

  nProbes = 0;
  Ccnt = Pcnt = Hcnt = 0;
  useTestRecord = false;
  diskData = strncmp(fileName, "/dev/", 5) ? true : false;

#ifdef PNG
  if (gzipped)
    {
    gzread(gz_fd, buffer, 2);
    gzseek(gz_fd, 0, SEEK_SET);	// gzrewind does not seem to work on
    }
  else
#endif
    {
    fread(buffer, 2, 1, fp);
    rewind(fp);
    }

  if ((buffer[0] = 'C' || buffer[0] == 'P') && isdigit(buffer[1]))
    {
    hdr = NULL;
    hasRAFheader = false;
    printf("No RAF header found, assuming raw PMS2D file.\n");
    }
  else
    {
    hdr = new Header(fileName);
    hasRAFheader = true;

    for (p = hdr->GetFirst("PMS2D"); p; p = hdr->GetNext("PMS2D"))
      {
      name = hdr->VariableName((Pms2 *)p);

      if (name[3] == 'P')
        probe[nProbes++] = new Probe(hdr, (Pms2 *)p, ++Pcnt);
      else
      if (name[3] == 'C')
        probe[nProbes++] = new Probe(hdr, (Pms2 *)p, ++Ccnt);
      else
      if (name[3] == 'H')
        probe[nProbes++] = new Probe(hdr, (Pms2 *)p, ++Hcnt);
      }
    }

  buildIndices();

  currLR = -1; currPhys = 0;

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void ADS_DataFile::ToggleSyntheticData()
{
  int		i, j;
  ulong		*p;
  ushort	*s;

  useTestRecord = 1 - useTestRecord;

  strcpy((char *)&CtestRecord.id, "C1");
  CtestRecord.hour = 12;
  CtestRecord.minute = 30;
  CtestRecord.second = 30;
  CtestRecord.tas = 100 * 255 / 125;
  CtestRecord.msec = 100;
  CtestRecord.overld = 36;

  p = (ulong *)CtestRecord.data;
  for (i = 0; i < 48; ++i)
    for (j = 0; j < 21; ++j)
      *p++ = CtestParticle[j];

  for (j = 0; j < 16; ++j)
    *p++ = CtestParticle[j];


  strcpy((char *)&PtestRecord.id, "P1");
  PtestRecord.hour = 12;
  PtestRecord.minute = 30;
  PtestRecord.second = 30;
  PtestRecord.tas = 100 * 255 / 125;
  PtestRecord.msec = 100;
  PtestRecord.overld = 30;

  p = (ulong *)PtestRecord.data;
  for (i = 0; i < 78; ++i)
    for (j = 0; j < 13; ++j)
      *p++ = PtestParticle[j];

  for (j = 0; j < 10; ++j)
    *p++ = PtestParticle[j];


  strcpy((char *)&HtestRecord.id, "H1");
  HtestRecord.hour = 12;
  HtestRecord.minute = 30;
  HtestRecord.second = 30;
  HtestRecord.tas = 100 * 255 / 125;
  HtestRecord.msec = 100;
  HtestRecord.overld = 30;

  s = (ushort *)HtestRecord.data;
  for (i = 0; i < 204; ++i)
    for (j = 0; j < 10; ++j)
      *s++ = HtestParticle[j];

  for (j = 0; j < 8; ++j)
    *s++ = HtestParticle[j];

}	/* END TOGGLESYNTHETICDATA */

/* -------------------------------------------------------------------- */
void ADS_DataFile::SetPosition(int position)
{
  int		pos;
  P2d_rec	buff;

  pos = nIndices * position / 100;

  if (pos == nIndices)
    --pos;

  LocatePMS2dRecord(&buff, ntohs(indices[pos].time[0]),
	ntohs(indices[pos].time[1]), ntohs(indices[pos].time[2]));

}	/* END SETPOSITION */

/* -------------------------------------------------------------------- */
bool ADS_DataFile::LocatePMS2dRecord(P2d_rec *buff, int hour, int minute, int second)
{
  int	i;
  bool	rc, startPreMidnight = False;

  if (ntohs(indices[0].time[0]) > 12)
    startPreMidnight = True;

  for (i = 1; indices[i].index > 0 && ntohs(indices[i].time[0]) < hour; ++i)
    if (startPreMidnight && ntohs(indices[i].time[0]) < 12 && hour > 12)
      hour -= 24;

  for (; indices[i].index > 0 && ntohs(indices[i].time[1]) < minute; ++i)
    ;

  for (; indices[i].index > 0 && ntohs(indices[i].time[2]) < second; ++i)
    ;

  if (indices[i].index == -1)
    return(false);

  currPhys = std::max(0, i - 2);
  currLR = P2DLRPR;
  rc = NextPMS2dRecord(buff);

  while (rc && ntohs(buff->second) < second)
    rc = NextPMS2dRecord(buff);

  SwapPMS2D(buff);
  return(rc);

}	/* END LOCATEPMS2DRECORD */

/* -------------------------------------------------------------------- */
bool ADS_DataFile::FirstPMS2dRecord(P2d_rec *buff)
{
  currPhys = currLR = 0;

  if (useTestRecord)
    {
    memcpy((char *)buff, (char *)&CtestRecord, sizeof(P2d_rec));
    return(true);
    }

  if (indices[0].index == -1)	// No 2d records in file.
    return(false);

#ifdef PNG
  if (gzipped)
    {
    gzseek(gz_fd, indices[0].index, SEEK_SET);
    gzread(gz_fd, physRecord, sizeof(P2d_rec) * P2DLRPR);
    }
  else
#endif
    {
    fseek(fp, indices[0].index, SEEK_SET);
    fread(physRecord, sizeof(P2d_rec), P2DLRPR, fp);
    }

  memcpy((char *)buff, (char *)physRecord, sizeof(P2d_rec));
  SwapPMS2D(buff);
  return(true);

}	/* END FIRSTPMS2DRECORD */

/* -------------------------------------------------------------------- */
bool ADS_DataFile::NextPMS2dRecord(P2d_rec *buff)
{
  if (useTestRecord)
    {
    if (testRecP == &CtestRecord)
      testRecP = &PtestRecord;
    else
    if (testRecP == &PtestRecord)
      testRecP = &HtestRecord;
    else
      testRecP = &CtestRecord;

    testRecP->msec += 80;
    if (testRecP->msec >= 1000)
      {
      testRecP->msec -= 1000;
      if (++testRecP->second > 59)
        ++testRecP->minute;
      }

    memcpy((char *)buff, (char *)testRecP, sizeof(P2d_rec));
    return(true);
    }

  if (++currLR >= P2DLRPR)
    {
    currLR = 0;

    if (indices[++currPhys].index == -1)
      {
      --currPhys;
      return(false);
      }

#ifdef PNG
    if (gzipped)
      {
      gzseek(gz_fd, indices[currPhys].index, SEEK_SET);
      gzread(gz_fd, physRecord, sizeof(P2d_rec) * P2DLRPR);
      }
    else
#endif
      {
      fseek(fp, indices[currPhys].index, SEEK_SET);
      fread(physRecord, sizeof(P2d_rec), P2DLRPR, fp);
      }
    }

  memcpy((char *)buff, (char *)&physRecord[currLR], sizeof(P2d_rec));
  SwapPMS2D(buff);
  return(true);

}	/* END NEXTPMS2DRECORD */

/* -------------------------------------------------------------------- */
bool ADS_DataFile::PrevPMS2dRecord(P2d_rec *buff)
{
  if (useTestRecord)
    {
    if (testRecP == &CtestRecord)
      testRecP = &PtestRecord;
    else
      testRecP = &CtestRecord;

    testRecP->msec -= 80;
    if (testRecP->msec < 0)
      {
      testRecP->msec += 1000;
      if (--testRecP->second < 0)
        --testRecP->minute;
      }

    memcpy((char *)buff, (char *)testRecP, sizeof(P2d_rec));
    return(false);
    }

  if (--currLR < 0)
    {
    currLR = P2DLRPR-1;

    if (--currPhys < 0)
      {
      currLR = 0;
      currPhys = 0;
      return(false);
      }

#ifdef PNG
    if (gzipped)
      {
      gzseek(gz_fd, indices[currPhys].index, SEEK_SET);
      gzread(gz_fd, physRecord, sizeof(P2d_rec) * P2DLRPR);
      }
    else
#endif
      {
      fseek(fp, indices[currPhys].index, SEEK_SET);
      fread(physRecord, sizeof(P2d_rec), P2DLRPR, fp);
      }
    }

  memcpy((char *)buff, (char *)&physRecord[currLR], sizeof(P2d_rec));
  SwapPMS2D(buff);
  return(true);

}	/* END PREVPMS2DRECORD */

/* -------------------------------------------------------------------- */
int ADS_DataFile::NextPhysicalRecord(char buff[])
{
  int	rc, idWord;
  int	size = sizeof(short);

#ifdef PNG
  if (gzipped)
    {
    savePos = gztell(gz_fd);
    rc = gzread(gz_fd, buff, size) / size;
    }
  else
#endif
    {
    savePos = ftell(fp);
//  if ((nBytes = read(fileno(fp), buff, size)) == 0 && GetNextADSfile())
    rc = fread(buff, size, 1, fp);
    }

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

    case 0x4d43:      // MCR
      size = sizeof(Mcr_rec) - sizeof(short);
      break;

    case PMS2DC1: case PMS2DC2: /* PMS2D */
    case PMS2DP1: case PMS2DP2:
    case PMS2DH1: case PMS2DH2: /* HVPS */
      size = PMS2_RECSIZE - sizeof(short);
      break;

    case PMS2DG1: case PMS2DG2: /* GrayScale */
      size = 32000 - sizeof(short);
      break;

    default:
      size = 0;
    }

#ifdef PNG
  if (gzipped)
    {
    if (gzread(gz_fd, &buff[sizeof(short)], size) != size)
      size = 0;
    }
  else
#endif
    {
    if (fread(&buff[sizeof(short)], size, 1, fp) != 1)
      size = 0;
    }

  return(size + sizeof(short));

}	/* END NEXTPHYSICALRECORD */

/* -------------------------------------------------------------------- */
void ADS_DataFile::buildIndices()
{
  int	i, cnt, rc;
  short	*word;
  FILE	*fpI;
  char	buffer[0x8000], *p, tmpFile[256];


  strcpy(tmpFile, fileName);

  if ((p = strstr(tmpFile, ".2d")) == NULL)
    strcat(tmpFile, ".2Didx");
  else
    strcpy(p, ".2Didx");


  // Check for indices file....
  if ( (fpI = fopen(tmpFile, "rb")) )
    {
    long	len;

    fseek(fpI, 0, SEEK_END);
    len = ftell(fpI);

    if ((indices = (Index *)malloc(len)) == NULL)
      {
      fprintf(stderr, "buildIndices: Memory allocation error, fatal.\n");
      exit(1);
      }

    printf("Reading indices file, %s.\n", tmpFile);

    rewind(fpI);
    fread(indices, len, 1, fpI);
    fclose(fpI);

    if (5 != ntohl(5))		// If Intel architecture, swap bytes.
      for (i = 0; i < len / sizeof(Index); ++i)
        indices[i].index = ntohl(indices[i].index);

    nIndices = (len / sizeof(Index)) - 1;
    return;
    }


  printf("Building indices...."); fflush(stdout);
  FlushEvents();

  word = (short *)buffer;

  if ((indices = (Index *)malloc(50000 * sizeof(Index))) == NULL)
    {
    fprintf(stderr, "buildIndices: Memory allocation error, fatal.\n");
    exit(1);
    }

#ifdef PNG
  if (gzipped)
    gzseek(gz_fd, 0, SEEK_SET);
  else
#endif
    rewind(fp);


  for (cnt = 0; rc = NextPhysicalRecord(buffer); )
    {
    if (hasRAFheader)
      {
      for (i = 0; i < nProbes; ++i)
        if (strcmp(probe[i]->Code, buffer) == 0)
          break;

      if (i == nProbes)	// shouldn't get here?
        continue;
      }
    else
      {
      for (i = 0; i < nProbes; ++i)
        if (strcmp(probe[i]->Code, buffer) == 0)
          break;

      if (i == nProbes)
        probe[nProbes++] = new Probe(buffer, PMS2_RECSIZE);
      }

    for (i = 0; i < 1; ++i)
      {
      indices[cnt].index = savePos + (sizeof(P2d_rec) * i);
      memcpy(indices[cnt].time, &buffer[2], 6);
      ++cnt;
      }
    }

#ifdef PNG
  if (gzipped)
    gzseek(gz_fd, 0, SEEK_SET);
  else
#endif
    rewind(fp);

  printf("\n%d 2d records were found.\n", cnt);

  indices[cnt].index = -1;

  if ((indices = (Index *)realloc(indices, (cnt+1) * sizeof(Index))) == NULL)
    {
    fprintf(stderr, "buildIndices: Memory re-allocation error, fatal.\n");
    exit(1);
    }

//  SortIndices(cnt);

/* Write new 2d file.  Used to fix IDEAS-III files that were out of time order.
    {

    }
 */


  // Write indices to a file for future use.
  if ( hasRAFheader && (fpI = fopen(tmpFile, "w+b")) )
    {
    printf("Writing indices file, %s.\n", tmpFile);

    if (5 != ntohl(5))		// If Intel architecture, swap bytes.
      for (i = 0; i < cnt+1; ++i)
        indices[i].index = htonl(indices[i].index);

    fwrite(indices, (cnt+1) * sizeof(Index), 1, fpI);
    fclose(fpI);

    if (5 != ntohl(5))		// Swap em back for current run.
      for (i = 0; i < cnt+1; ++i)
        indices[i].index = ntohl(indices[i].index);
    }

  nIndices = cnt;

}	/* END BUILDINDICES */

/* -------------------------------------------------------------------- */
void ADS_DataFile::SwapPMS2D(P2d_rec *buff)
{
  // Perform byte swapping on whole [data] record if required.
  if (1 != ntohs(1))
    {
    ulong       *p;
    ushort       *sp = (ushort *)buff;

    for (int i = 1; i < 10; ++i)
      sp[i] = ntohs(sp[i]);

    p = (ulong *)buff->data;
    sp = (ushort *)buff->data;

    if (((char *)&buff->id)[0] == 'H')
      for (int i = 0; i < 2048; ++i, ++sp)
        *sp = ntohs(*sp);
    else
      for (int i = 0; i < 1024; ++i, ++p)
        *p = ntohl(*p);
    }
}

/* -------------------------------------------------------------------- */
void ADS_DataFile::SortIndices(int cnt)
{
  sort_the_table(0, cnt-1);
                                                                                     
}       /* SORTTABLE */
                                                                                     
/* -------------------------------------------------------------------- */
void ADS_DataFile::sort_the_table(int beg, int end)
{
  Index	*mid, temp;
  int	x = beg, y = end;
                                                                                     
  mid = &indices[(x + y) / 2];
                                                                                     
  while (x <= y)
    {
    while (memcmp(indices[x].time, mid->time, 6) < 0)
      ++x;
                                                                                     
    while (memcmp(indices[y].time, mid->time, 6) > 0)
      --y;
                                                                                     
    if (x <= y)
      {
      temp = indices[x];
      indices[x] = indices[y];
      indices[y] = temp;
                                                                                     
      ++x;
      --y;
      }
    }
                                                                                     
  if (beg < y)
    sort_the_table(beg, y);
                                                                                     
  if (x < end)
    sort_the_table(x, end);

}

/* -------------------------------------------------------------------- */
ADS_DataFile::~ADS_DataFile()
{
  free(indices);

#ifdef PNG
  if (gzipped)
    gzclose(gz_fd);
  else
#endif
    fclose(fp);

}	/* END DESTRUCTOR */

/* END DATAFILE.CC */
