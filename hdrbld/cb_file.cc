/*
-------------------------------------------------------------------------
OBJECT NAME:	cb_file.c

FULL NAME:	File Menu Callbacks

ENTRY POINTS:	OpenNewFile()
		OpenNewFile_OK()
		SaveFile()
		SaveFileAs()
		SaveQuit()
		Print()
		Quit()

STATIC FNS:	OpenNewFile_Q()
		WriteHeader()

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1995
-------------------------------------------------------------------------
*/

#include "hdrbld.h"
#include "hardwire.h"
#include "portable.h"
#include "pms.h"

#include <Xm/TextF.h>
#include <Xm/ToggleB.h>


static void	OpenNewFile_Q();
static int	WriteHeader(char s[]), RateGroupSDI(int s);
static bool	Quiting = False, OutstandingWarnings = False;


/* -------------------------------------------------------------------- */
void OpenNewFile(Widget w, XtPointer client, XtPointer call)
{
  if (ChangesMade)
    WarnUser("You have not saved this file.", OpenNewFile_Q, NULL);
  else
    OpenNewFile_Q();

}

/* -------------------------------------------------------------------- */
static void OpenNewFile_Q()
{
  sprintf(buffer, "%s/*/header", ProjectDirectory);
  QueryFile("Enter file name to load:", buffer, OpenNewFile_OK);

}

/* -------------------------------------------------------------------- */
void OpenNewFile_OK(	Widget w,
			XtPointer client,
			XmFileSelectionBoxCallbackStruct *call)
{
  int		i, j;
  FILE		*fp, *fp1;
  char		tmp[64];

  Blk		*blk = (Blk *)buffer;
  Asy		*asyn = (Asy *)buffer;
  Sh		*sh = (Sh *)buffer;
  Pms1v2	*pmsV2 = (Pms1v2 *)buffer;
  Pms1v3	*pmsV3 = (Pms1v3 *)buffer;
  Pms2		*pms2d = (Pms2 *)buffer;

  if (w)
    {
    char	*file;

    ExtractFileName(call->value, &file);
    FileCancel((Widget)NULL, (XtPointer)NULL, (XtPointer)NULL);

    strcpy(FileName, file);
    }


  if ((fp = fopen(FileName, "rb")) == NULL)
    {
    fprintf(stderr, "Can't open %s.\n", FileName);
    return;
    }

  fread((char *)&flightInfo, sizeof(Fl), 1, fp);


  /* Clear out old project.
   */
  for (i = 0; i < nsdi; ++i)
    free(sdi[i]);

  nsdi = 0;
  Inertial[0] = Inertial[1] = GPS[0] = GPS[1] = GPS[2] = 0;
  SetPrimaryInertial(NULL, (XtPointer)Inertial[0], NULL);
  SetSecondaryInertial(NULL, (XtPointer)Inertial[1], NULL);
  SetPrimaryGPS(NULL, (XtPointer)GPS[0], NULL);
  SetSecondaryGPS(NULL, (XtPointer)GPS[1], NULL);
  SetTertiaryGPS(NULL, (XtPointer)GPS[2], NULL);

  for (i = 0; other[i].title; ++i)
    for (j = 0; j < 2; ++j)
      XmToggleButtonSetState(other[i].toggleB[j], FALSE, TRUE);

  for (i = 0; asy[i].title; ++i)
    XmToggleButtonSetState(asy[i].toggleB[0], FALSE, TRUE);



  /* Check for validity of header, and current version #.
   */
  if (strcmp(flightInfo.thdr, TAPEHDR_STR) != 0)
    {
    ShowError("Invalid header file.");
    ProjectNumber = NULL;
    XmTextFieldSetString(projText[0], "");
    XmTextFieldSetString(projText[1], "");
    fclose(fp);
    return;
    }

  if (atof(flightInfo.version) < 3.0)
    {
    ShowError("hdrbld does NOT support old ADS headers.");
    ProjectNumber = NULL;
    XmTextFieldSetString(projText[0], "");
    XmTextFieldSetString(projText[1], "");
    fclose(fp);
    return;
    }


  ProjectNumber = flightInfo.prnum;
  XmTextFieldSetString(projText[0], ProjectNumber);

  for (i = 0; aircraft[i]; ++i)
    if (strcmp(aircraft[i], flightInfo.acraft) == 0)
      SetAircraft(NULL, (XtPointer)i, NULL);

  SetDSMlist(flightInfo.acraft);


  /* Read ProjectName file.
   */
  sprintf(buffer, "%s/%s/ProjectName", ProjectDirectory, ProjectNumber);
  if ((fp1 = fopen(buffer, "r")) != NULL)
    {
    fgets(ProjectName, 64, fp1);
    fclose(fp1);

    if (ProjectName[strlen(ProjectName)-1] == '\n')
      ProjectName[strlen(ProjectName)-1] = '\0';

    XmTextFieldSetString(projText[1], ProjectName);
    }
  else
    XmTextFieldSetString(projText[1], "");



  /* Read struct Sh's.
   */
/*printf("Name      Start  Length  Rate  Addr  type  Offset  DSM\n"); */
  while (fread(buffer, 12, 1, fp) == 1)
    {
    fread(&buffer[12], ntohl(blk->item_len)-12, 1, fp);

    if (strcmp(blk->item_type, SDI_STR) == 0)
      {
      if (strcmp(sh->name, "DUMMY") == 0)
        continue;

      sdi[nsdi] = (Sh *)GetMemory(sizeof(Sh));

      sh->start = ntohl(sh->start);
      sh->rate = ntohl(sh->rate);
      sh->adsaddr = ntohl(sh->adsaddr);
      sh->order = ntohl(sh->order);
      sh->ch_gain = ntohl(sh->ch_gain);
      sh->ch_offset = ntohl(sh->ch_offset);
      sh->convert_offset = ntohl(sh->convert_offset);
      sh->convert = ntohf(sh->convert);

      for (i = 0; i < sh->order; ++i)
        sh->cof[i] = ntohf(sh->cof[i]);

      memcpy((char *)sdi[nsdi], buffer, ntohl(sh->item_len));

/*printf("%-10s %5d %4d   %4d  %4d    %c    %4d    %s\n",
	sdi[nsdi]->name, sdi[nsdi]->start, sdi[nsdi]->length, sdi[nsdi]->rate,
	sdi[nsdi]->adsaddr, sdi[nsdi]->type[0], sdi[nsdi]->offset,
	sdi[nsdi]->dsm_locn);
*/
      ++nsdi;
      continue;
      }



    /* Navigation, Inertial then GPS.
     */
    for (i = 1; inertial[i].blkName; ++i)
      if (strcmp(blk->item_type, inertial[i].blkName) == 0)
        {
        if (!Inertial[0])
          {
          Inertial[0] = i;
          SetPrimaryInertial(NULL, (XtPointer)Inertial[0], NULL);
          SetMenu(navDSMom[0], blk->dsm_locn);
          }
        else
          {
          Inertial[1] = i;
          SetSecondaryInertial(NULL, (XtPointer)Inertial[1], NULL);
          SetMenu(navDSMom[1], blk->dsm_locn);
          }
        }

    for (i = 1; gps[i].blkName; ++i)
      if (strcmp(blk->item_type, gps[i].blkName) == 0)
        {
        if (!GPS[0])
          {
          GPS[0] = i;
          SetPrimaryGPS(NULL, (XtPointer)GPS[0], NULL);
          SetMenu(navDSMom[2], blk->dsm_locn);
          }
        else if (!GPS[1])
          {
          GPS[1] = i;
          SetSecondaryGPS(NULL, (XtPointer)GPS[1], NULL);
          SetMenu(navDSMom[3], blk->dsm_locn);
          }
        else
          {
          GPS[2] = i;
          SetTertiaryGPS(NULL, (XtPointer)GPS[2], NULL);
          SetMenu(navDSMom[4], blk->dsm_locn);
          }
        }

    /* PMS probes.
     */
    if (strcmp(blk->item_type, PMS1V2_STR) == 0)
      {
      int	indx;

      indx = LocatePMSlocn(pmsV2->locn);
      SetMenu(pmsInfo[indx].probe, pmsV2->serial_num);
      SetPMS(NULL, (XtPointer)indx, NULL);
      SetMenu(pmsInfo[indx].DSMom, pmsV2->dsm_locn);

      sprintf(tmp, "%d", ntohl(pmsV2->intf_num));
      SetMenu(pmsInfo[indx].interfaceNum, tmp);
      sprintf(tmp, "%d", ntohl(pmsV2->intf_chan)+1);
      SetMenu(pmsInfo[indx].channelNum, tmp);
      }

    if (strcmp(blk->item_type, PMS1V3_STR) == 0)
      {
      int	indx;

      indx = LocatePMSlocn(pmsV3->locn);
      SetMenu(pmsInfo[indx].probe, pmsV3->serial_num);
      SetPMS(NULL, (XtPointer)indx, NULL);
      SetMenu(pmsInfo[indx].DSMom, pmsV3->dsm_locn);

      sprintf(tmp, "%d", 0);
      SetMenu(pmsInfo[indx].interfaceNum, tmp);
      sprintf(tmp, "%d", ntohl(pmsV3->intf_chan));
      SetMenu(pmsInfo[indx].channelNum, tmp);
      }

    /* PMS 2D */
    if (strcmp(blk->item_type, PMS2D_STR) == 0)
      {
      int	indx;

      indx = LocatePMSlocn(pms2d->locn);
      SetMenu(pmsInfo[indx].probe, pms2d->serial_num);
      SetPMS(NULL, (XtPointer)indx, NULL);
      SetMenu(pmsInfo[indx].DSMom, pms2d->dsm_locn);

      sprintf(tmp, "%d", 0);
      SetMenu(pmsInfo[indx].interfaceNum, tmp);
      sprintf(tmp, "%d", ntohl(pms2d->intf_chan)+1);
      SetMenu(pmsInfo[indx].channelNum, tmp);
      }



    /* Other probes.
     */
    for (i = 0; other[i].title; ++i)
      {
      if (strcmp(blk->item_type, other[i].blkName) == 0)
        {
        if (XmToggleButtonGetState(other[i].toggleB[0]))
          {
          XmToggleButtonSetState(other[i].toggleB[1], TRUE, TRUE);
          SetMenu(other[i].DSMom[1], blk->dsm_locn);
          }
        else
          {
          XmToggleButtonSetState(other[i].toggleB[0], TRUE, TRUE);
          SetMenu(other[i].DSMom[0], blk->dsm_locn);
          }
        }
      }

    /* Async probes.
     */
    if (strcmp(blk->item_type, ASYNC_STR) == 0)
      {
      for (i = 0; asy[i].title; ++i)
        if (strcmp(asyn->name, asy[i].blkName) == 0)
          XmToggleButtonSetState(asy[i].toggleB[0], TRUE, TRUE);
      }
    }

  fclose(fp);

  ClearCurrentSh(NULL, NULL, NULL);
  FillListWidget();
  ChangesMade = FALSE;

}	/* END OPENNEWFILE_OK */

/* -------------------------------------------------------------------- */
void SaveFileAs(Widget w, XtPointer client, XtPointer call)
{
  sprintf(buffer, HEADER, ProjectDirectory, ProjectNumber);
  QueryFile("Save as:", buffer, SaveFileAs_OK);

}

/* -------------------------------------------------------------------- */
void SaveQuit(Widget w, XtPointer client, XtPointer call)
{
  Quiting = True;

  SaveFile(NULL, NULL, NULL);

  if (!OutstandingWarnings)
    Quit(NULL, NULL, NULL);

  Quiting = OutstandingWarnings = False;

}

/* -------------------------------------------------------------------- */
void SaveFileAs_OK(Widget w, XtPointer client, XmFileSelectionBoxCallbackStruct *call)
{
  char    *file;

  ExtractFileName(call->value, &file);
  FileCancel((Widget)NULL, (XtPointer)NULL, (XtPointer)NULL);

  if (WriteHeader(file) == ERR)
    ShowError("Error trying to save, aborted.");
  else
    ChangesMade = FALSE;

}

/* -------------------------------------------------------------------- */
void SaveFile(Widget w, XtPointer client, XtPointer call)
{
  if (WriteHeader(NULL) == ERR)
    ShowError("Error trying to save, aborted.");
  else
    ChangesMade = FALSE;

}

/* -------------------------------------------------------------------- */
static int WriteHeader(char file[])
{
  FILE	*fp;
  int	i, j;
  int	start, rateCnt, rate, nBins;
  char	*p, *sn, backupFile[512];
  bool	mustCalAirplane = False;

  Fl		portableFl;
  Sh		portableSh;
  Asy		asyn;
  Blk		blk;
  Evt		evt;
  Pms1v2	pmsV2;
  Pms1v3	pmsV3;
  Pms2		pms2d;
  Pms2h		pms2h;


  if (ProjectNumber == NULL || atoi(ProjectNumber) < 100)
    {
    fprintf(stderr, "Invalid Project Number, please enter new.\n");
    return(ERR);
    }


  if (file)
    strcpy(FileName, file);
  else
    sprintf(FileName, "%s/%s/header", ProjectDirectory, ProjectNumber);


  /* Save old header (1 level only).
   */
  sprintf(backupFile, "%s.bak", FileName);
  rename(FileName, backupFile);


  if ((fp = fopen(FileName, "w+b")) == NULL)
    {
    fprintf(stderr, "Can't open %s\n", FileName);
    return(ERR);
    }

  if (nsdi > 1)
    SortSh();

  strcpy(flightInfo.thdr, TAPEHDR_STR);
  strcpy(flightInfo.version, VERSION_STR);
  strcpy(flightInfo.prnum, ProjectNumber);
  strcpy(flightInfo.acraft, GetMenu(acOpMenu));
  strcpy(flightInfo.tzone, "UTC");
  strcpy(flightInfo.ads_type, ADS_TYPE_2_STR);
  flightInfo.item_len = sizeof(Fl);
  flightInfo.thdrlen = sizeof(Fl);
  fwrite((char *)&flightInfo, sizeof(Fl), 1, fp);

  start = 0;

  /* Write HDR Blk.
   */
  strcpy(blk.item_type, HDR_STR);
  blk.item_len = htonl(sizeof(Blk));
  blk.start = htonl(start);
  blk.length = htonl(sizeof(Hdr_blk));
  blk.rate = htonl(1);
  strcpy(blk.locn, "");
  strcpy(blk.dsm_locn, DSM_CTL_STR);
	
  start += sizeof(Hdr_blk);
  flightInfo.n_items = 1;
  flightInfo.thdrlen += sizeof(Blk);

  fwrite((char *)&blk, sizeof(Blk), 1, fp);


  /* Write SDI blocks.  Determine # per rate group first.
   */
  start = RateGroupSDI(sizeof(Hdr_blk));

  if (start % 4)
    {
    sdi[nsdi] = (Sh *)GetMemory(sizeof(Sh));
    *sdi[nsdi] = *sdi[nsdi-1];

    strcpy(sdi[nsdi]->name, "DUMMY");
    strcpy(sdi[nsdi]->type, typeListChar[0]);
    sdi[nsdi]->rate = 1;
    sdi[nsdi]->adsaddr = 0x3f;
    ++nsdi;
    }

  flightInfo.n_items = 1;
  flightInfo.thdrlen = sizeof(Fl) + sizeof(Blk);
  start = RateGroupSDI(sizeof(Hdr_blk));


/*printf("Name      Start  Length  Rate  Addr  type  Offset  DSM\n");*/
  for (i = 0; i < nsdi; ++i)
    {
    if (sdi[i]->type[0] != 'A')
      {
      sdi[i]->convert = 1.0;
      sdi[i]->convert_offset = 0;
      }

    portableSh = *sdi[i];

    if (sdi[i]->type[0] == 'A' &&
	sdi[i]->convert_offset == 0 && sdi[i]->convert == 0.0)
      {
      mustCalAirplane = True;
      if (Quiting)
        OutstandingWarnings = True;
      }

    portableSh.item_len = htonl(sdi[i]->item_len);
    portableSh.start = htonl(sdi[i]->start);
    portableSh.length = htonl(sdi[i]->length);
    portableSh.rate = htonl(sdi[i]->rate);
    portableSh.adsaddr = htonl(sdi[i]->adsaddr);
    portableSh.offset = htonl(sdi[i]->offset);
    portableSh.order = htonl(sdi[i]->order);
    portableSh.ch_gain = htonl(sdi[i]->ch_gain);
    portableSh.ch_offset = htonl(sdi[i]->ch_offset);
    portableSh.convert_offset = htonl(sdi[i]->convert_offset);
    portableSh.convert = htonf(sdi[i]->convert);

    for (j = 0; j < sdi[i]->order; ++j)
      portableSh.cof[j] = htonf(sdi[i]->cof[j]);

    fwrite((char *)&portableSh, sizeof(Sh), 1, fp);

/*printf("%-10s %5d %4d   %4d  %4d    %c    %4d    %s\n",
    sdi[i]->name, sdi[i]->start, sdi[i]->length, sdi[i]->rate,
    sdi[i]->adsaddr, sdi[i]->type[0], sdi[i]->offset,
    sdi[i]->dsm_locn);*/
    }


  if (nsdi > 0 && strcmp(sdi[nsdi-1]->name, "DUMMY") == 0)
    {
    free(sdi[nsdi-1]);
    --nsdi;
    }


  /* Navigation Intruments.
   */
/*  if (Inertial[0])
    {
    Irs	irs;

    strcpy(irs.item_type, IRS_STR);
    irs.item_len = htonl(sizeof(Irs));
    irs.start = htonl(start);
    irs.length = htonl(inertial[Inertial[0]].blk_len);

    if (Inertial[1])
      strcpy(irs.locn, "PITL");
    else
      strcpy(irs.locn, "CAB");

    p = GetMenu(navDSMom[0]);
    strcpy(irs.dsm_locn, p);
    XtFree(p);

    fwrite((char *)&irs, sizeof(Irs), 1, fp);
    start += inertial[Inertial[0]].blk_len;
    ++flightInfo.n_items;
    flightInfo.thdrlen += sizeof(Irs);
    }

  if (Inertial[1])
    {
    Irs	irs;

    strcpy(irs.item_type, IRS_STR);
    irs.item_len = htonl(sizeof(Irs));
    irs.start = htonl(start);
    irs.length = htonl(inertial[Inertial[1]].blk_len);
    strcpy(irs.locn, "PITR");

    p = GetMenu(navDSMom[1]);
    strcpy(irs.dsm_locn, p);
    XtFree(p);

    fwrite((char *)&irs, sizeof(Irs), 1, fp);
    start += inertial[Inertial[0]].blk_len;
    ++flightInfo.n_items;
    flightInfo.thdrlen += sizeof(Irs);
    }
*/
  for (i = 0; i < 2 && Inertial[i]; ++i)
    {
    int	hdr_len;

    if (inertial[Inertial[i]].blkName[0] == 'C')  // CMidgets.
      hdr_len = sizeof(Blk);
    else
      hdr_len = sizeof(Irs);

    strcpy(blk.item_type, inertial[Inertial[i]].blkName);
    blk.item_len = htonl(hdr_len);
    blk.start = htonl(start);
    blk.length = htonl(inertial[Inertial[i]].blk_len);
    blk.rate = htonl(1);
    strcpy(blk.locn, irsLocns[i]);

    p = GetMenu(navDSMom[i]);
    strcpy(blk.dsm_locn, p);
    XtFree(p);

    fwrite((char *)&blk, hdr_len, 1, fp);
    start += inertial[Inertial[i]].blk_len;
    ++flightInfo.n_items;
    flightInfo.thdrlen += hdr_len;
    }


  for (i = 0; i < 3 && GPS[i]; ++i)
    {
    strcpy(blk.item_type, gps[GPS[i]].blkName);
    blk.item_len = htonl(sizeof(Blk));
    blk.start = htonl(start);
    blk.length = htonl(gps[GPS[i]].blk_len);
    blk.rate = htonl(1);
    strcpy(blk.locn, gpsLocns[i]);

    p = GetMenu(navDSMom[i+2]);
    strcpy(blk.dsm_locn, p);
    XtFree(p);

    fwrite((char *)&blk, sizeof(Blk), 1, fp);
    start += gps[GPS[i]].blk_len;
    ++flightInfo.n_items;
    flightInfo.thdrlen += sizeof(Blk);
    }


  /* PMS probes.
   */
  rate = 10;
  for (i = 0; pmsInfo[i].title && pmsInfo[i].enabled; ++i)
    {
    sn = GetMenu(pmsInfo[i].probe);

    if (strcmp(sn, "None") == 0)
      continue;

    if (strncmp(GetPMSparameter(sn, "TYPE"), "2D", 2) == 0)
      {
      strcpy(pms2d.item_type, PMS2D_STR);
      strcpy(pms2h.item_type, PMS2DH_STR);
      pms2d.item_len = htonl(sizeof(Pms2));
      pms2h.item_len = htonl(sizeof(Pms2h));
      strcpy(pms2d.name, GetPMSparameter(sn, "TYPE"));
      strcpy(pms2h.name, GetPMSparameter(sn, "TYPE"));
      strcpy(pms2d.locn, pmsInfo[i].abbrev);
      strcpy(pms2h.locn, pmsInfo[i].abbrev);
      strcpy(pms2d.serial_num, GetMenu(pmsInfo[i].probe));
      strcpy(pms2h.serial_num, GetMenu(pmsInfo[i].probe));
      strcpy(pms2d.dsm_locn, GetMenu(pmsInfo[i].DSMom));
      strcpy(pms2h.dsm_locn, GetMenu(pmsInfo[i].DSMom));

      pms2h.start = htonl(start);
      pms2h.length = htonl(sizeof(P2d_house));
      pms2d.resolution = htons(atoi(GetPMSparameter(sn, "RANGE_STEP")));
      pms2d.lrlen = htonl(sizeof(P2d_rec));
      pms2d.lrppr = htonl(7);
      pms2d.intf_chan = htonl(atoi(GetMenu(pmsInfo[i].channelNum)) - 1);
      pms2h.intf_chan = htonl(atoi(GetMenu(pmsInfo[i].channelNum)) - 1);

      for (j = 0; j < P2D_HOUSE; ++j)
        {
        int     k;
        char    temp[32], temp1[512];

        sprintf(temp, "HSKP%d", j);
        p = GetPMSparameter(sn, temp);
        strcpy(temp1, p);
        p = strtok(temp1, " \t\n");
        strcpy(pms2h.hsk_name[j], p);

        for (k = 0; k < P1DV2_COF; ++k)
          {
          p = strtok(NULL, " \t\n");
          pms2h.hsk_cof[j][k] = htonf(atof(p));
          }
        }

      fwrite((char *)&pms2h, sizeof(Pms2h), 1, fp);
      fwrite((char *)&pms2d, sizeof(Pms2), 1, fp);
      flightInfo.thdrlen += sizeof(Pms2h);
      flightInfo.thdrlen += sizeof(Pms2);
      flightInfo.n_items += 2;
      start += sizeof(Pms2h);
      }
    else	/* PMS1V2 */
    if (strncmp(GetPMSparameter(sn, "TYPE"), "S", 1))
      {
      strcpy(pmsV2.item_type, PMS1V2_STR);
      pmsV2.item_len	= htonl(sizeof(Pms1v2));
      pmsV2.start	= htonl(start);
      pmsV2.rate	= htonl(rate);
      pmsV2.ps_start	= htonl(0);
      pmsV2.ps_length	= htonl(0);
      pmsV2.intf_num	= htonl(atoi(GetMenu(pmsInfo[i].interfaceNum)));
      pmsV2.intf_chan	= htonl(atoi(GetMenu(pmsInfo[i].channelNum)) - 1);

      strcpy(pmsV2.locn, pmsInfo[i].abbrev);
      strcpy(pmsV2.serial_num, GetMenu(pmsInfo[i].probe));
      strcpy(pmsV2.dsm_locn, GetMenu(pmsInfo[i].DSMom));
      strcpy(pmsV2.name, GetPMSparameter(sn, "TYPE"));

      if (strcmp(pmsV2.name, F300_STR) == 0)
        {
        pmsV2.length = htonl(sizeof(P32v2_blk) * rate);
        start += sizeof(P32v2_blk) * rate;
        }
      else
      if (strcmp(pmsV2.name, X260_STR) == 0)
        {
        pmsV2.length = htonl(sizeof(P64v2_blk) * rate);
        start += sizeof(P64v2_blk) * rate;
        }
      else
        {
        pmsV2.length = htonl(sizeof(P16v2_blk) * rate);
        start += sizeof(P16v2_blk) * rate;
        }

      for (j = 0; j < P1DV2_AUX; ++j)
        {
        int	k;
	char	temp[32], temp1[512];

        sprintf(temp, "HSKP%d", j);
        p = GetPMSparameter(sn, temp);
        strcpy(temp1, p);
        p = strtok(temp1, " \t\n");
        strcpy(pmsV2.hsk_name[j], p);

        for (k = 0; k < P1DV2_COF; ++k)
          {
          p = strtok(NULL, " \t\n");
          pmsV2.hsk_cof[j][k] = htonf(atof(p));
          }
        }

      fwrite((char *)&pmsV2, sizeof(Pms1v2), 1, fp);
      ++flightInfo.n_items;
      flightInfo.thdrlen += sizeof(Pms1v2);
      }
    else	/* PMS1D V3 */
      {
      strcpy(pmsV3.item_type, PMS1V3_STR);
      pmsV3.item_len = htonl(sizeof(Pms1v3));
      pmsV3.start = htonl(start);
      pmsV3.rate = htonl(rate);
      pmsV3.intf_chan = htonl(atoi(GetMenu(pmsInfo[i].channelNum)));

      // Set them up with defaults first, then try to read from PMSspecs.
      pmsV3.threshold = htonl(0x14);
      pmsV3.transRej = htonl(0x01);
      pmsV3.dofRej = htonl(0x01);
      pmsV3.avgTransWt = htonl(0x05);
      pmsV3.attAccept = htonl(0x5f);
      pmsV3.divisorFlag = htonl(0x00);
      pmsV3.ct_method = htonl(0x00);
      pmsV3.max_width = htonl(10000);

      if ((p = GetPMSparameter(sn, "THRESHOLD")) )
        pmsV3.threshold = htonl(atoi(p));

      if ((p = GetPMSparameter(sn, "TRANSIT_REJ")) )
        pmsV3.transRej = htonl(atoi(p));

      if ((p = GetPMSparameter(sn, "DOF_REJ")) )
        pmsV3.dofRej = htonl(atoi(p));

      if ((p = GetPMSparameter(sn, "AVG_TRANSIT_WGT")) )
        pmsV3.avgTransWt = htonl(atoi(p));

      if ((p = GetPMSparameter(sn, "ATT_ACCEPT")) )
        pmsV3.attAccept = htonl(atoi(p));

      if ((p = GetPMSparameter(sn, "DIVISOR_FLAG")) )
        pmsV3.divisorFlag = htonl(atoi(p));

      if ((p = GetPMSparameter(sn, "CT_METHOD")) )
        pmsV3.ct_method = htonl(atoi(p));

      if ((p = GetPMSparameter(sn, "MAX_WIDTH")) )
        pmsV3.max_width = htonl(atoi(p));


      if ((p = GetPMSparameter(sn, "NCHANNELS")) == NULL)
        {
        fprintf(stderr, "hdrbld: No NCHANNELS in PMSspecs file for %s.\n",
					GetMenu(pmsInfo[i].probe));
        pmsV3.bins = nBins = 0;
        }
      else
        {
        nBins = atoi(p);
        pmsV3.bins = htonl(nBins);
        }

      if ((p = GetPMSparameter(sn, "RANGE")) == NULL)
        {
        fprintf(stderr, "hdrbld: No RANGE in PMSspecs file for %s.\n",
					GetMenu(pmsInfo[i].probe));
        pmsV3.defaultRange = 0;
        }
      else
        {
        pmsV3.defaultRange = htonl(atoi(p));
        }


      sprintf(buffer, "THRESHOLDS_%d", nBins);
      if ((p = GetPMSparameter(sn, buffer)) == NULL)
        {
        fprintf(stderr, "hdrbld: No %s in PMSspecs file for %s.\n",
					buffer, GetMenu(pmsInfo[i].probe));
        memset(&pmsV3.OPCthreshold, 0, sizeof(pmsV3.OPCthreshold));
        }
      else
        {
        strcpy(buffer, p);
        p = strtok(buffer, ", \t\n");

        for (j = 0; j < nBins; ++j)
          {      
          pmsV3.OPCthreshold[j] = p ? htons(atoi(p)) : 0;
          p = strtok(NULL, ", \t\n");
          }      
        }

      strcpy(pmsV3.locn, pmsInfo[i].abbrev);
      strcpy(pmsV3.serial_num, GetMenu(pmsInfo[i].probe));
      strcpy(pmsV3.dsm_locn, GetMenu(pmsInfo[i].DSMom));
      strcpy(pmsV3.name, GetPMSparameter(sn, "TYPE"));

      if (strcmp(pmsV3.name, SPP100_STR) == 0)
        {
        pmsV3.length = htonl(sizeof(Spp100_blk));
        start += sizeof(Spp100_blk);
        }
      else
      if (strcmp(pmsV3.name, SPP200_STR) == 0)
        {
        pmsV3.length = htonl(sizeof(Spp200_blk));
        start += sizeof(Spp200_blk);
        }
      else
      if (strcmp(pmsV3.name, SPP300_STR) == 0)
        {
        pmsV3.length = htonl(sizeof(Spp300_blk));
        start += sizeof(Spp300_blk);
        }

      fwrite((char *)&pmsV3, sizeof(Pms1v3), 1, fp);
      ++flightInfo.n_items;
      flightInfo.thdrlen += sizeof(Pms1v3);
      }
    }



  /* Other
   */
  for (i = 0; other[i].title; ++i)
    for (j = 0; j < 2; ++j)
      {
      if (XmToggleButtonGetState(other[i].toggleB[j]) == FALSE)
        continue;

      strcpy(blk.item_type, other[i].blkName);
      blk.item_len = htonl(sizeof(Blk));
      blk.start = htonl(start);
      blk.length = htonl(other[i].blk_len);
      blk.rate = htonl(other[i].rate);
      strcpy(blk.locn, "");

      p = GetMenu(other[i].DSMom[j]);
      strcpy(blk.dsm_locn, p);
      XtFree(p);

      fwrite((char *)&blk, sizeof(Blk), 1, fp);
      start += other[i].blk_len;
      ++flightInfo.n_items;
      flightInfo.thdrlen += sizeof(Blk);
      }


  /* Async
   */
  for (i = 0; asy[i].title; ++i)
    {
    if (XmToggleButtonGetState(asy[i].toggleB[0]) == FALSE)
      continue;

    strcpy(asyn.item_type, ASYNC_STR);
    asyn.item_len = htonl(sizeof(Asy));
    strcpy(asyn.name, asy[i].blkName);
    asyn.lrlen = htonl(0);
    asyn.lrppr = htonl(1);
    strcpy(asyn.dsm_locn, "CTL");

    fwrite((char *)&asyn, sizeof(Asy), 1, fp);
    ++flightInfo.n_items;
    flightInfo.thdrlen += sizeof(Asy);
    }


  /* Do Events.
   */
#define BLK_LEN	4

  strcpy(evt.item_type, EVNT_STR);
  strcpy(evt.dsm_locn, DSM_CTL_STR);
  evt.item_len = htonl(sizeof(Evt));
  evt.length = htonl(BLK_LEN);

  for (i = 0; eventLocns[i]; ++i)
    {
    evt.start = htonl(start);
    strcpy(evt.locn, eventLocns[i]);

    fwrite((char *)&evt, sizeof(Evt), 1, fp);
    start += BLK_LEN;
    ++flightInfo.n_items;
    flightInfo.thdrlen += sizeof(Evt);
    }


  /* Re-write Fl struct.
   */
  flightInfo.lrlen = start;
  flightInfo.lrppr = 1;

  memcpy(&portableFl, &flightInfo, sizeof(Fl));
  portableFl.item_len = htonl(flightInfo.item_len);
  portableFl.n_items = htonl(flightInfo.n_items);
  portableFl.lrlen = htonl(flightInfo.lrlen);
  portableFl.lrppr = htonl(flightInfo.lrppr);
  portableFl.thdrlen = htonl(flightInfo.thdrlen);
  
  rewind(fp);
  fwrite((char *)&portableFl, sizeof(Fl), 1, fp);
  fclose(fp);

/*printf("nItems=%ld, lrlen=%ld, lrppr=%ld, thdrlen=%ld\n",
		flightInfo.n_items,
		flightInfo.lrlen,
		flightInfo.lrppr,
		flightInfo.thdrlen);
 */

  /* Read ProjectName file.
   */
  sprintf(buffer, "%s/%s/ProjectName", ProjectDirectory, ProjectNumber);
  if ((fp = fopen(buffer, "w+")) != NULL)
    {
    p = XmTextFieldGetString(projText[1]);
    fprintf(fp, "%s\n", p);
    fclose(fp);
    XtFree(p);
    }


  DumpToChangeLog(FileName);

  if (mustCalAirplane)
    {
    fprintf(stderr, "\n>>> Airplane requires A/D calibrations. <<<\n\n");

    if (Quiting)
      WarnUser("Airplane requires A/D calibrations.", Quit, NULL);
    else
      WarnUser("Airplane requires A/D calibrations.", NULL, NULL);
    }

  return(OK);

}	/* END WRITEHEADER */

/* -------------------------------------------------------------------- */
int RateGroupSDI(int start)
{
  int	i, j, rateCnt;

  for (rateCnt = i = 0; i < nsdi; ++i)
    {
    if (i == 0 || sdi[i]->rate == sdi[i-1]->rate)
      {
      ++rateCnt;
      }
    else
      {
      if (sdi[i-1]->rate != 5000)
        start += (rateCnt * sdi[i-1]->rate * sizeof(short)) -
                (rateCnt * sizeof(short));

      for (j = i-rateCnt; j < i; ++j)
        sdi[j]->offset = rateCnt * sizeof(short);

      rateCnt = 1;
      }

    strcpy(sdi[i]->item_type, SDI_STR);
    sdi[i]->item_len = sizeof(Sh);
    sdi[i]->start = start;
    sdi[i]->length = sizeof(short);
    if (sdi[i]->rate != 5000)
      start += sizeof(short);
    ++flightInfo.n_items;
    flightInfo.thdrlen += sizeof(Sh);
    }


  if (nsdi > 0)
    {
    start += (rateCnt * sdi[i-1]->rate * sizeof(short)) - (rateCnt * sizeof(short));

    for (j = i-rateCnt; j < i; ++j)
      sdi[j]->offset = rateCnt * sizeof(short);
    }

  return(start);

}

/* -------------------------------------------------------------------- */
void Print(Widget w, XtPointer client, XtPointer call)
{
  printf("hdrbld: Printing not supported yet.\n");

}

/* -------------------------------------------------------------------- */
void Quit(Widget w, XtPointer client, XtPointer call)
{
  if (ChangesMade)
    {
    WarnUser("You have not saved this file.", exit, NULL);
    return;
    }

  exit(0);
}

/* END CB_FILE.C */
