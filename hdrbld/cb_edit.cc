/*
-------------------------------------------------------------------------
OBJECT NAME:	cb_edit.c

FULL NAME:	Callbacks for SDI edit area.

ENTRY POINTS:	EditVariable()
		Search()
		Search_OK()
		Accept()
		Delete()
		FillListWidget()
		ShowBlock()
		ValidateVarName()
		MapCalCof()

STATIC FNS:	CreateListLineItem()

DESCRIPTION:	

REFERENCES:	

REFERENCED BY:	

COPYRIGHT:	University Corporation for Atmospheric Research, 1996-2000
-------------------------------------------------------------------------
*/

#include "hdrbld.h"
#include "hardwire.h"
#include "vardb.h"

#include <Xm/List.h>
#include <Xm/TextF.h>


static XmString CreateListLineItem(Sh *);


/* -------------------------------------------------------------------- */
void Search_OK(Widget w, XtPointer client, XtPointer call)
{
  int	i;

  QueryCancel(NULL, NULL, NULL);
  ExtractAnswer(buffer);
  strupr(buffer);

  for (i = 0; i < nsdi; ++i)
    {
    if (strcmp(sdi[i]->name, buffer) == 0)
      {
      XmListSetPos(varList, i);
      XmListSelectPos(varList, i+1, FALSE);
      }
    }

}	/* END SEARCH_OK */

/* -------------------------------------------------------------------- */
void Search(Widget w, XtPointer client, XtPointer call)
{
  QueryUser("Enter variable to search for:", 20, Search_OK);

}	/* END SEARCH */

/* -------------------------------------------------------------------- */
void EditVariable(Widget w, XtPointer client, XmListCallbackStruct *call)
{
  int	i;
  int	indx = call->item_position - 1;
  char	tbuf[20];


  memcpy((char *)&currentSh, (char *)sdi[indx], sizeof(Sh));

  XmTextFieldSetString(varText, currentSh.name);

  for (i = 0; DSM[i]; ++i)
    if (strcmp(DSM[i], currentSh.dsm_locn) == 0)
      SetSDI_DSM(NULL, (XtPointer)i, NULL);

  for (i = 0; typeListChar[i]; ++i)
    if (strcmp(typeListChar[i], currentSh.type) == 0)
      SetSDI_Type(NULL, (XtPointer)i, NULL);

  for (i = 0; sampleRates[i]; ++i)
    {
    sprintf(tbuf, "%ld", currentSh.rate);
    if (strcmp(sampleRates[i], tbuf) == 0)
      SetSDI_SampleRate(NULL, (XtPointer)i, NULL);
    }

  for (i = 0; i < 0x107; ++i)
    {
    if (i == currentSh.adsaddr)
      SetSDI_CardAddr(NULL, (XtPointer)i, NULL);
    }

  for (i = 0; gains[i]; ++i)
    {
    sprintf(tbuf, "%ld", currentSh.ch_gain);
    if (strcmp(gains[i], tbuf) == 0)
      SetSDI_Gain(NULL, (XtPointer)i, NULL);
    }

  for (i = 0; offsets[i]; ++i)
    {
    sprintf(tbuf, "%ld", currentSh.ch_offset);
    if (strcmp(offsets[i], tbuf) == 0)
      SetSDI_Offset(NULL, (XtPointer)i, NULL);
    }


  for (i = 0; i < currentSh.order; ++i)
    {
    sprintf(buffer, "%e", currentSh.cof[i]);
    XmTextFieldSetString(calText[i], buffer);
    }

  for (; i < MX_COF; ++i)
    XmTextFieldSetString(calText[i], "");

}

/* -------------------------------------------------------------------- */
void Accept(Widget w, XtPointer client, XtPointer call)
{
  int		i;
  char		*p, *name;

  name = XmTextFieldGetString(varText);

  if (strlen(name) == 0)
    return;

  if (currentSh.ch_gain == 1 && currentSh.ch_offset != 0)
    {
    ShowError("You may not have an offset with a gain of 1, not accepted.");
    return;
    }

  for (i = 0; i < nsdi; ++i)
    if (strcmp(currentSh.type, sdi[i]->type) == 0 &&
	currentSh.adsaddr == sdi[i]->adsaddr &&
	strcmp(currentSh.name, sdi[i]->name) &&
	strcmp(currentSh.dsm_locn, sdi[i]->dsm_locn) == 0)
      {
      ShowError("Duplicate address, not accepted.");
      return;
      }


  ChangesMade = TRUE;

  for (i = 0; i < MX_COF; ++i)
    {
    p = XmTextFieldGetString(calText[i]);

    currentSh.cof[i] = atof(p);
    XtFree(p);
    }

  for (i = MX_COF-1; i > 1; --i)
    if (currentSh.cof[i] != 0.0)
      {
      currentSh.order = i + 1;
      break;
      }

  if (currentSh.type[0] != 'A')
    {
    currentSh.convert = 1.0;
    currentSh.convert_offset = 0;
    }

  for (i = 0; i < nsdi; ++i)
    if (strcmp(sdi[i]->name, name) == 0)
      break;

  if (i == nsdi)	/* New variable		*/
    {
    sdi[i] = (Sh *)GetMemory(sizeof(Sh));
    memcpy((char *)sdi[i], (char *)&currentSh, sizeof(Sh));
    strcpy(sdi[i]->name, name);
    sdi[i]->convert = 0.0;
    sdi[i]->convert_offset = 0;
    sdi[++nsdi] = NULL;

    sprintf(buffer, "%s added to analog/digital list.\n", sdi[i]->name);
    AddToChangeLog(buffer);
    }
  else
    {
    sprintf(buffer, "%s modified in analog/digital list.\n", sdi[i]->name);
    AddToChangeLog(buffer);
    DiffSDI(sdi[i], &currentSh);

    memcpy((char *)sdi[i], (char *)&currentSh, sizeof(Sh));
    }


  Clear(NULL, NULL, NULL);
  SortSh();
  FillListWidget();

}

/* -------------------------------------------------------------------- */
void Clear(Widget w, XtPointer client, XtPointer call)
{
  ClearCurrentSh(w, client, call);

}

/* -------------------------------------------------------------------- */
void Delete(Widget w, XtPointer client, XtPointer call)
{
  int	i, *pos_list, pos_cnt = 0;

  XmListGetSelectedPos(varList, &pos_list, &pos_cnt);

  if (pos_cnt == 0)
    return;

  --nsdi;

  i = pos_list[0] - 1;

  sprintf(buffer, "%s deleted from analog/digital list.\n", sdi[i]->name);
  AddToChangeLog(buffer);

  free((char *)sdi[i]);

  for (; i < nsdi; ++i)
    sdi[i] = sdi[i+1];

  Clear(NULL, NULL, NULL);
  SortSh();
  FillListWidget();
  XmListSelectPos(varList, pos_list[0], TRUE);

}

/* -------------------------------------------------------------------- */
void ShowBlock(Widget w, XtPointer client, XtPointer call)
{
  static Widget	prevBlk = NULL;

  if (((XmToggleButtonCallbackStruct *)call)->set)
    {
    if (prevBlk != NULL)
      XtUnmanageChild(prevBlk);

    XtManageChild((Widget)client);

    prevBlk = (Widget)client;
    }
    
}

/* -------------------------------------------------------------------- */
void FillListWidget()
{
  int		i, firstVisPos;
  Arg		args[5];
  XmString	line[MX_SDI];

  i = 0;
  XtSetArg(args[i], XmNtopItemPosition, &firstVisPos); ++i;
  XtGetValues(varList, args, i);

  XmListDeleteAllItems(varList);

  for (i = 0; i < nsdi; ++i)
    line[i] = CreateListLineItem(sdi[i]);

  XmListAddItems(varList, line, nsdi, 0);

  XmListSetPos(varList, firstVisPos);
//  XmListSelectPos(varList, pos+1, FALSE);

}	/* END FILLLISTWIDGET */

/* -------------------------------------------------------------------- */
static XmString CreateListLineItem(Sh *cd)
{
  int		i;
  char	tbuf[20];

  strcpy(tbuf, cd->name);

  if (VarDB_lookup(cd->name) == ERR)
    strcat(tbuf, "*");

  sprintf(buffer, "%-10s %-8s %-3s %5ld %4lx %3ld %3ld  ",
		tbuf, cd->dsm_locn, cd->type, cd->rate, cd->adsaddr,
		cd->ch_gain, cd->ch_offset);

  for (i = 0; i < cd->order; ++i)
    {
    sprintf(tbuf, " %13e", cd->cof[i]);
    strcat(buffer, tbuf);
    }

  return(XmStringCreateLocalized(buffer));

}

/* -------------------------------------------------------------------- */
void ValidateVarName(Widget w, XtPointer client, XtPointer call)
{
  char	*p;

  p = XmTextFieldGetString(varText);
  strupr(p);
  XmTextFieldSetString(varText, p);
  XtFree(p);
}

/* -------------------------------------------------------------------- */
void MapCalCof(Widget w, XtPointer client, XtPointer call)
{
  char    *p;
 
  p = XmTextFieldGetString(w);
  sprintf(buffer, "%e", atof(p));
  XmTextFieldSetString(w, buffer);
 
  XtFree(p);
 
}   /* END MAPCALCOE */

/* END CCB.C */
