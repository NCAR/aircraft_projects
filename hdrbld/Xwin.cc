/*
-------------------------------------------------------------------------
OBJECT NAME:	Xwin.c

FULL NAME:	Create X window GUI

ENTRY POINTS:	CreateMainWindow()
		InitializeAircraft()
		InitializeStaticOpMenus()
		InitSDI()
		InitNavInstruments()
		InitPMSprobes()
		InitOtherProbes()

STATIC FNS:	CreateDSMmenu()

DESCRIPTION:	

INPUT:		

OUTPUT:		

REFERENCES:	none

REFERENCED BY:	hdrbld.c (main)

COPYRIGHT:	University Corporation for Atmospheric Research, 1996-2000
-------------------------------------------------------------------------
*/

#include <unistd.h>
#include <sys/types.h>

#include <Xm/CascadeB.h>
#include <Xm/Form.h>
#include <Xm/Frame.h>
#include <Xm/Label.h>
#include <Xm/List.h>
#include <Xm/PushB.h>
#include <Xm/RowColumn.h>
#include <Xm/Separator.h>
#include <Xm/ToggleB.h>
#include <Xm/TextF.h>

#include "hdrbld.h"
#include "hardwire.h"
#include "ac.h"
#include "pms.h"

#define N_ADDRS	263

struct menu
        {
        char            *title;
        void            (*callback)(Widget, XtPointer, XtPointer);
        XtPointer       callData;
        } ;

static struct menu      fileMenu[] = {
	{ "openNewFile", OpenNewFile, NULL },
	{ "saveFile", SaveFile, NULL },
	{ "saveFileAs", SaveFileAs, NULL },
	{ "print", Print, NULL },
	{ "savequit", SaveQuit, NULL },
	{ "quit", Quit, NULL },
	{ NULL, NULL, NULL }};

static struct menu      editMenu[] = {
	{ "search", Search, NULL },
	{ "seperator", NULL, NULL },
	{ "editVarDB", EditVarDB, NULL },
	{ "editDepend", EditProjectFile, "DependTable" },
	{ "editDefaults", EditProjectFile, "Defaults" },
	{ "editDespike", EditProjectFile, "Despike" },
	{ "editLags", EditProjectFile, "Lags" },
	{ "editPMS", EditProjectFile, "PMSspecs" },
	{ "editAsciiParms", EditProjectFile, "ascii_parms" },
	{ "seperator", NULL, NULL },
	{ "vinet", EditProjectFile, "netconfig" },
	{ "editRegions", EditDefaultFile, "regions" },
	{ "editAC", EditDefaultFile, "AircraftSpecs" },
	{ "editDSM", EditHostsFile, "dsmconfig" },
	{ NULL, NULL, NULL }};

static struct menu      projMenu[] = {
	{ "create", CreateProject, NULL },
	{ "transOnboard", forkXterm, "XferOnboard" },
	{ "transInhouse", forkXterm, "XferInhouse" },
	{ NULL, NULL, NULL }};

static struct menu      transMenu[] = {
	{ "xferADSrel", forkXterm4xfer, "XferADSrel" },
	{ "xferNIMrel", forkXterm4xfer, "XferNIMrel" },
	{ "xferWINDSrel", forkXterm4xfer, "XferWINDSrel" },
	{ "xferProjDefs", forkXterm4xfer, "XferProjDefs" },
	{ "xferLibs", forkXterm4xfer, "XferLibs" },
	{ "xfervxWorks", forkXterm4xfer, "XferVxWorks" },
	{ "seperator", NULL, NULL },
	{ "xferADSdev", forkXterm4xfer, "XferADSdev" },
	{ "xferNIMdev", forkXterm4xfer, "XferNIMdev" },
	{ "xferWINDSdev", forkXterm4xfer, "XferWINDSdev" },
	{ NULL, NULL, NULL }};

static struct
        {
        char            *title;
        struct menu     *sub;
        } main_menu[] = {
                { "File", fileMenu },
                { "Edit", editMenu },
                { "Proj Chores", projMenu },
                { "Transfer(s)", transMenu },
                { NULL, NULL }};


/* Global widget declarations.
 */
Widget	projText[2], projFileText;

Widget	acOpMenu, acPD, acButts[8];
Widget	blockButtonFrame, blockFrame[12];

Widget	varText, SDIpd[6], SDIom[6], calText[MX_COF], sdiDSMbutts[MAX_DSM],
	typeButts[4], srButts[8], cardAddrButts[N_ADDRS], gainButts[5],
	offsetButts[2], varList;

Widget	navTypeOM[MAX_NAV], navDSMom[MAX_NAV];

static void InitializeAircraft(Widget opmenu);
static void InitializeStaticOpMenus();
static void CreateDSMmenu(Widget, Widget *, Widget *);


/* -------------------------------------------------------------------- */
Widget CreateMainWindow(Widget parent)
{
  int		i, j;
  Arg		args[32];
  Cardinal	n;
  XmString	name;
  Widget	topLevelForm;
  Widget	menuBar, menu[6], menu_button[6];
  Widget	b[16];
  Widget	projFrame, projRC, form[2], label[2];
  Widget	blockRB;

  n = 0;
  topLevelForm = XmCreateForm(parent, "topLevelForm", args, n);


  /* Create Menus
   */
  n = 0;
  menuBar = XmCreateMenuBar(topLevelForm, "menuBar", args, n);
  XtManageChild(menuBar);


  for (i = 0; main_menu[i].title; ++i)
    {
    n = 0;
    menu[i] = XmCreatePulldownMenu(menuBar, main_menu[i].title, args, n);

    n = 0;
    XtSetArg(args[n], XmNsubMenuId, menu[i]); ++n;
    menu_button[i] = XmCreateCascadeButton(menuBar, main_menu[i].title, args,n);

    for (j = 0; main_menu[i].sub[j].title; ++j)
      {
      n = 0;

      if (main_menu[i].sub[j].callback == NULL)
        {
        b[j] = XmCreateSeparator(menu[i], main_menu[i].sub[j].title,args,n);
        continue;
        }

      b[j] = XmCreatePushButton(menu[i], main_menu[i].sub[j].title, args, n);
      XtAddCallback(b[j], XmNactivateCallback,
              main_menu[i].sub[j].callback, main_menu[i].sub[j].callData);
      }

    XtManageChildren(b, j);
    }

  XtManageChildren(menu_button, i);


  /* Only ADS & CHRIS get to use transfer menu.
   */
  if (geteuid() != 110)
    XtSetSensitive(menu[i-1], FALSE);


  /* Aircraft Menu.
   */
  n = 0;
  acPD = XmCreatePulldownMenu(topLevelForm, "acPullDown", args, n);

  n = 0;
  XtSetArg(args[n], XmNleftAttachment, XmATTACH_WIDGET); n++;
  XtSetArg(args[n], XmNleftWidget, menuBar); n++;
  XtSetArg(args[n], XmNtopAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNsubMenuId, acPD); ++n;
  acOpMenu = XmCreateOptionMenu(topLevelForm, "acOpMenu", args, n);
  XtManageChild(acOpMenu);

  InitializeAircraft(acPD);


  /* Header Dump button
   */
  n = 0;
  XtSetArg(args[n], XmNtopAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNrightAttachment, XmATTACH_FORM); n++;
  b[0] = XmCreatePushButton(topLevelForm, "hdrDump", args, n);
  XtManageChild(b[0]);
  XtAddCallback(b[0], XmNactivateCallback, HeaderDump, NULL);


  /* Project info Frame/Form.
   */
  n = 0;
  XtSetArg(args[n], XmNtopAttachment, XmATTACH_WIDGET); n++;
  XtSetArg(args[n], XmNtopWidget, menuBar); n++;
  XtSetArg(args[n], XmNleftAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNrightAttachment, XmATTACH_FORM); n++;
  projFrame = XmCreateFrame(topLevelForm, "projFrame", args, n);
  XtManageChild(projFrame);

  n = 0;
  projRC = XmCreateRowColumn(projFrame, "projRC", args, n);
  XtManageChild(projRC);

  n = 0;
  form[0] = XmCreateRowColumn(projRC, "fieldRC", args, n);
  form[1] = XmCreateRowColumn(projRC, "fieldRC", args, n);
  XtManageChildren(form, 2);

  n = 0;
  label[0] = XmCreateLabel(form[0], "projNumber", args, n);
  label[1] = XmCreateLabel(form[1], "projName", args, n);
  XtManageChild(label[0]);
  XtManageChild(label[1]);

  n = 0;
  projText[0] = XmCreateTextField(form[0], "projNumText", args, n);
  projText[1] = XmCreateTextField(form[1], "projNameText", args, n);
  XtManageChild(projText[0]);
  XtManageChild(projText[1]);
  XtAddCallback(projText[0], XmNlosingFocusCallback, SetProject, NULL);



  /* Block Probe Buttons.
   */
  n = 0;
  XtSetArg(args[n], XmNtopAttachment, XmATTACH_WIDGET); n++;
  XtSetArg(args[n], XmNtopWidget, projFrame); n++;
  XtSetArg(args[n], XmNleftAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNrightAttachment, XmATTACH_FORM); n++;
  blockButtonFrame = XmCreateFrame(topLevelForm, "blockButtonFrame", args, n);
  XtManageChild(blockButtonFrame);

  n = 0;
  blockRB = XmCreateRadioBox(blockButtonFrame, "blockRB", args, n);
  XtManageChild(blockRB);

  for (i = 0; blockButtons[i].blockType; ++i)
    {
    name = XmStringCreateLocalized(blockButtons[i].blockType);

    n = 0;
    XtSetArg(args[n], XmNlabelString, name); ++n;
    b[i] = XmCreateToggleButton(blockRB, "blockBut", args, n);

    XmStringFree(name);

    n = 0;
    XtSetArg(args[n], XmNtopAttachment, XmATTACH_WIDGET); n++;
    XtSetArg(args[n], XmNtopWidget, blockButtonFrame); n++;
    XtSetArg(args[n], XmNleftAttachment, XmATTACH_FORM); n++;
    XtSetArg(args[n], XmNbottomAttachment, XmATTACH_FORM); n++;
    if (i < 2)
      XtSetArg(args[n], XmNrightAttachment, XmATTACH_FORM); n++;
    blockFrame[i] = XmCreateFrame(topLevelForm, "blockFrame", args, n);

    XtAddCallback(b[i], XmNvalueChangedCallback, ShowBlock,
				(XtPointer)blockFrame[i]);

    (*blockButtons[i].initFn)(blockFrame[i]);
    }

  XtManageChildren(b, i);
  XmToggleButtonSetState(b[0], TRUE, TRUE);

  return(topLevelForm);

}	/* END CREATEMAINWINDOW */

/* -------------------------------------------------------------------- */
static void InitializeAircraft(Widget opmenu)
{
  int		i, n;
  Arg		args[8];
  XmString	name;


  /* Init Type.
   */
  for (i = 0; aircraft[i]; ++i)
    {
    name = XmStringCreateLocalized(aircraft[i]);

    n = 0;
    XtSetArg(args[n], XmNlabelString, name); ++n;
    acButts[i] = XmCreatePushButton(opmenu, "opMenB", args, n);
    XtAddCallback(acButts[i], XmNactivateCallback, SetAircraft, (XtPointer)i);

    XmStringFree(name);
    }

  XtManageChildren(acButts, i);

}

/* -------------------------------------------------------------------- */
static void InitializeStaticOpMenus()
{
  int		i, n;
  Arg		args[8];
  XmString	name;


  /* Init Type.
   */
  for (i = 0; typeList[i]; ++i)
    {
    name = XmStringCreateLocalized(typeList[i]);

    n = 0;
    XtSetArg(args[n], XmNlabelString, name); ++n;
    typeButts[i] = XmCreatePushButton(SDIpd[1], "opMenB", args, n);
    XtAddCallback(typeButts[i], XmNactivateCallback, SetSDI_Type, (XtPointer)i);

    XmStringFree(name);
    }

  XtManageChildren(typeButts, i);


  /* Init Sample Rates.
   */
  for (i = 0; sampleRates[i]; ++i)
    {
    name = XmStringCreateLocalized(sampleRates[i]);

    n = 0;
    XtSetArg(args[n], XmNlabelString, name); ++n;
    srButts[i] = XmCreatePushButton(SDIpd[2], "opMenB", args, n);
    XtAddCallback(srButts[i], XmNactivateCallback, SetSDI_SampleRate, (XtPointer)i);

    XmStringFree(name);
    }

  XtManageChildren(srButts, i);


  /* Init Card Addrs.
   */
  for (i = 0; i < N_ADDRS; ++i)
    {
    sprintf(buffer, "%x", i);
    name = XmStringCreateLocalized(buffer);

    n = 0;
    XtSetArg(args[n], XmNlabelString, name); ++n;
    cardAddrButts[i] = XmCreatePushButton(SDIpd[3], "opMenB", args, n);
    XtAddCallback(cardAddrButts[i], XmNactivateCallback, SetSDI_CardAddr, (XtPointer)i);

    XmStringFree(name);
    }

  XtManageChildren(cardAddrButts, i);


  /* Init Gains.
   */
  for (i = 0; gains[i]; ++i)
    {
    name = XmStringCreateLocalized(gains[i]);

    n = 0;
    XtSetArg(args[n], XmNlabelString, name); ++n;
    gainButts[i] = XmCreatePushButton(SDIpd[4], "opMenB", args, n);
    XtAddCallback(gainButts[i], XmNactivateCallback, SetSDI_Gain, (XtPointer)i);

    XmStringFree(name);
    }

  XtManageChildren(gainButts, i);


  /* Init Offsets.
   */
  for (i = 0; offsets[i]; ++i)
    {
    name = XmStringCreateLocalized(offsets[i]);

    n = 0;
    XtSetArg(args[n], XmNlabelString, name); ++n;
    offsetButts[i] = XmCreatePushButton(SDIpd[5], "opMenB", args, n);
    XtAddCallback(offsetButts[i], XmNactivateCallback, SetSDI_Offset, (XtPointer)i);

    XmStringFree(name);
    }

  XtManageChildren(offsetButts, i);

}

/* -------------------------------------------------------------------- */
void InitSDI(Widget frame)
{
  int		i;
  Cardinal	n;
  Arg		args[8];
  Widget	sdiForm, sdiRC, varNameRC, varLabel, calLabel, calRC, listFrame,
		acceptButton, deleteButton, clearButton;

  /* SDI Entry Form.
   */
  n = 0;
  sdiForm = XmCreateForm(frame, "sdiForm", args, n);
  XtManageChild(sdiForm);

  n = 0;
  XtSetArg(args[n], XmNtopAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNleftAttachment, XmATTACH_FORM); n++;
  sdiRC = XmCreateRowColumn(sdiForm, "sdiRC", args, n);
  XtManageChild(sdiRC);

  n = 0;
  varNameRC = XmCreateRowColumn(sdiRC, "sdiInfoRC", args, n);
  XtManageChild(varNameRC);

  n = 0;
  varLabel = XmCreateLabel(varNameRC, "varLabel", args, n);
  XtManageChild(varLabel);

  n = 0;
  varText = XmCreateTextField(varNameRC, "varText", args, n);
  XtAddCallback(varText, XmNlosingFocusCallback, ValidateVarName, NULL);
  XtManageChild(varText);


  /* 6 opMenus, ' DSM, Type, SR, Addr, Gain, Offset'.
   */
  for (i = 0; i < 6; ++i)
    {
    sprintf(buffer, "opMenuPD%d", i);
    n = 0;
    SDIpd[i] = XmCreatePulldownMenu(sdiRC, buffer, args, n);

    sprintf(buffer, "opMenu%d", i);
    n = 0;
    XtSetArg(args[n], XmNsubMenuId, SDIpd[i]); ++n;
    SDIom[i] = XmCreateOptionMenu(sdiRC, buffer, args, n);
    XtManageChild(SDIom[i]);
    }

  /* Scrolled List Widget for SDI.
   */
  n = 0;
  XtSetArg(args[n], XmNtopAttachment, XmATTACH_WIDGET); n++;
  XtSetArg(args[n], XmNtopWidget, sdiRC); n++;
  XtSetArg(args[n], XmNleftAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNbottomAttachment, XmATTACH_FORM); n++;
  listFrame = XmCreateFrame(sdiForm, "listFrame", args, n);
  XtManageChild(listFrame);

  n = 0;
  varList = XmCreateScrolledList(listFrame, "varList", args, n);
  XtAddCallback(varList, XmNbrowseSelectionCallback,
				(XtCallbackProc)EditVariable, 0);
  XtManageChild(varList);


  n = 0;
  XtSetArg(args[n], XmNtopAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNrightAttachment, XmATTACH_FORM); n++;
  XtSetArg(args[n], XmNleftAttachment, XmATTACH_WIDGET); n++;
  XtSetArg(args[n], XmNleftWidget, listFrame); n++;
  calRC = XmCreateRowColumn(sdiForm, "calRC", args, n);
  XtManageChild(calRC);

  n = 0;
  calLabel = XmCreateLabel(calRC, "calLabel", args, n);
  XtManageChild(calLabel);

  for (i = 0; i < MX_COF; ++i)
    {
    n = 0;
    calText[i] = XmCreateTextField(calRC, "calText", args, n);
    XtManageChild(calText[i]);
    XtAddCallback(calText[i], XmNlosingFocusCallback, MapCalCof, NULL);
    }

  n = 0;
  acceptButton = XmCreatePushButton(calRC, "acceptButton", args, n);
  XtAddCallback(acceptButton, XmNactivateCallback, Accept, (XtPointer)0);
  XtManageChild(acceptButton);

  n = 0;
  deleteButton = XmCreatePushButton(calRC, "deleteButton", args, n);
  XtAddCallback(deleteButton, XmNactivateCallback, Delete, (XtPointer)0);
  XtManageChild(deleteButton);

  n = 0;
  clearButton = XmCreatePushButton(calRC, "clearButton", args, n);
  XtAddCallback(clearButton, XmNactivateCallback, Clear, (XtPointer)0);
  XtManageChild(clearButton);

  InitializeStaticOpMenus();
  InitializeDSMmenu(SDIpd[0], DSM, SetSDI_DSM);

}	/* END INITSDI */

/* -------------------------------------------------------------------- */
void (*navCB[])(Widget, XtPointer, XtPointer) =
	{
	SetPrimaryInertial,
	SetSecondaryInertial,
	SetPrimaryGPS,
	SetSecondaryGPS,
	SetTertiaryGPS
	} ;

void InitNavInstruments(Widget frame)
{
  int		i, j, n;
  Arg		args[8];
  XmString	name;
  Widget	innerFrame, navRC;
  Widget	RC[MAX_NAV], label[MAX_NAV], b[8],
		navTypePD[MAX_NAV], navDSMpd[MAX_NAV];

  struct nav	*navP;

  n = 0;
  navRC = XmCreateRowColumn(frame, "navRC", args, n);
  XtManageChild(navRC);

  for (i = 0; i < MAX_NAV; ++i)
    {
    n = 0;
    innerFrame = XmCreateFrame(navRC, "innerFrame", args, n);
    XtManageChild(innerFrame);

    n = 0;
    RC[i] = XmCreateRowColumn(innerFrame, "navRCsub", args, n);
    XtManageChild(RC[i]);

    sprintf(buffer, "navLabel%d", i);
    n = 0;
    label[i] = XmCreateLabel(RC[i], buffer, args, n);
    XtManageChild(label[i]);


    n = 0;
    navTypePD[i] = XmCreatePulldownMenu(RC[i], "navTypePD", args, n);

    n = 0;
    XtSetArg(args[n], XmNsubMenuId, navTypePD[i]); ++n;
    navTypeOM[i] = XmCreateOptionMenu(RC[i], "navTypeOM", args, n);
    XtManageChild(navTypeOM[i]);

    if (i < 2)
      navP = inertial;
    else
      navP = gps;

    for (j = 0; navP[j].longName; ++j)
      {
      name = XmStringCreateLocalized(navP[j].longName);
 
      n = 0;
      XtSetArg(args[n], XmNlabelString, name); ++n;
      b[j] = XmCreatePushButton(navTypePD[i], "inertButt", args, n);
      XtAddCallback(b[j], XmNactivateCallback, navCB[i], (XtPointer)j);

      XmStringFree(name);
      }

    XtManageChildren(b, j);


    CreateDSMmenu(RC[i], &navDSMom[i], &navDSMpd[i]);
    InitializeDSMmenu(navDSMpd[i], DSM, NULL);
    }

  XtSetSensitive(navDSMom[1], FALSE);
  XtSetSensitive(navDSMom[3], FALSE);
  XtSetSensitive(navDSMom[4], FALSE);
  XtSetSensitive(navTypeOM[1], FALSE);
  XtSetSensitive(navTypeOM[3], FALSE);
  XtSetSensitive(navTypeOM[4], FALSE);

}	/* END INITNAVINSTRUMENTS */

/* -------------------------------------------------------------------- */
void InitPMSprobes(Widget frame)
{
  int		i, j, n, nProbes;
  char		*pmsProbes[128];
  Arg		args[8];
  XmString	name;
  Widget	RC, subFrame[MAX_LOCN], label[MAX_LOCN],
		probePD[MAX_PMS], DSMpd[MAX_PMS], intNumPD[MAX_PMS],
		chanNumPD[MAX_PMS], resPD[MAX_PMS], b[100];

  n = 0;
  RC = XmCreateRowColumn(frame, "pmsRC", args, n);
  XtManageChild(RC);


  for (i = 0; pmsInfo[i].title; ++i)
    {
    n = 0;
    subFrame[i] = XmCreateFrame(RC, "pmsFrames", args, n);
    XtManageChild(subFrame[i]);

    n = 0;
    pmsInfo[i].rc = XmCreateRowColumn(subFrame[i], "pmsProbeRC", args, n);
    XtManageChild(pmsInfo[i].rc);

    name = XmStringCreateLocalized(pmsInfo[i].title);
    n = 0;
    XtSetArg(args[n], XmNlabelString, name); ++n;
    label[i] = XmCreateLabel(pmsInfo[i].rc, "pmsLabel", args, n);
    XtManageChild(label[i]);
    XmStringFree(name);

    n = 0;
    probePD[i] = XmCreatePulldownMenu(pmsInfo[i].rc, "pmsProbePD", args, n);

    n = 0;
    XtSetArg(args[n], XmNsubMenuId, probePD[i]); ++n;
    pmsInfo[i].probe = XmCreateOptionMenu(pmsInfo[i].rc, "pmsProbeOM", args, n);
    XtManageChild(pmsInfo[i].probe);


    /* Add all probes to menu.
     */
    nProbes = GetPMSlist(pmsProbes);

    name = XmStringCreateLocalized("None");
    n = 0;
    XtSetArg(args[n], XmNlabelString, name); ++n;
    b[0] = XmCreatePushButton(probePD[i], "pmsButt", args, n);
    XtManageChild(b[0]);
    XtAddCallback(b[0], XmNactivateCallback, SetPMS, (XtPointer)i);
    XmStringFree(name);

    for (j = 0; j < nProbes; ++j)
      {
      name = XmStringCreateLocalized(pmsProbes[j]);

      n = 0;
      XtSetArg(args[n], XmNlabelString, name); ++n;
      b[j] = XmCreatePushButton(probePD[i], "pmsButt", args, n);
      XtAddCallback(b[j], XmNactivateCallback, SetPMS, (XtPointer)i);

      XmStringFree(name);
      }

    XtManageChildren(b, nProbes);

    CreateDSMmenu(pmsInfo[i].rc, &pmsInfo[i].DSMom, &DSMpd[i]);
    InitializeDSMmenu(DSMpd[i], DSM, NULL);
    XtSetSensitive(pmsInfo[i].DSMom, FALSE);


    /* Interface & Channel numbers.
     */
    n = 0;
    intNumPD[i] = XmCreatePulldownMenu(pmsInfo[i].rc, "pmsIntPD", args, n);
    chanNumPD[i] = XmCreatePulldownMenu(pmsInfo[i].rc, "pmsChanPD", args, n);
    resPD[i] = XmCreatePulldownMenu(pmsInfo[i].rc, "pmsResPD", args, n);

    n = 0;
    XtSetArg(args[n], XmNsubMenuId, intNumPD[i]); ++n;
    pmsInfo[i].interfaceNum = XmCreateOptionMenu(pmsInfo[i].rc, "pmsIntOM", args, n);
    XtManageChild(pmsInfo[i].interfaceNum);

    for (j = 0; j < 2; ++j)
      {
      sprintf(buffer, "%d", j);
      name = XmStringCreateLocalized(buffer);

      n = 0;
      XtSetArg(args[n], XmNlabelString, name); ++n;
      b[j] = XmCreatePushButton(intNumPD[i], "pmsButt", args, n);
      XmStringFree(name);
      }

    XtManageChildren(b, 2);

    n = 0;
    XtSetArg(args[n], XmNsubMenuId, chanNumPD[i]); ++n;
    pmsInfo[i].channelNum = XmCreateOptionMenu(pmsInfo[i].rc, "pmsChanOM", args, n);
    XtManageChild(pmsInfo[i].channelNum);

    for (j = 0; j < 8; ++j)
      {
      sprintf(buffer, "%d", j+1);
      name = XmStringCreateLocalized(buffer);

      n = 0;
      XtSetArg(args[n], XmNlabelString, name); ++n;
      b[j] = XmCreatePushButton(chanNumPD[i], "pmsButt", args, n);
      XmStringFree(name);
      }

    XtManageChildren(b, 8);


    XtSetSensitive(pmsInfo[i].interfaceNum, FALSE);
    XtSetSensitive(pmsInfo[i].channelNum, FALSE);
    }

}	/* END INITPMSPROBES */

/* -------------------------------------------------------------------- */
void InitSerial(Widget frame)
{

}

/* -------------------------------------------------------------------- */
void InitClimet(Widget frame)
{

}

/* -------------------------------------------------------------------- */
void InitOtherProbes(Widget frame)
{
  int		i, j, n;
  Arg		args[8];
  XmString	name;
  Widget	otherRC, subFrame, subRC, otherDSMpd[MAX_OTHER];

  n = 0;
  otherRC = XmCreateRowColumn(frame, "otherRC", args, n);
  XtManageChild(otherRC);


  for (i = 0; other[i].title; ++i)
    {
    n = 0;
    subFrame = XmCreateFrame(otherRC, "otherFrames", args, n);
    XtManageChild(subFrame);

    n = 0;
    subRC = XmCreateRowColumn(subFrame, "otherProbeRC", args, n);
    XtManageChild(subRC);

    for (j = 0; j < 2; ++j)
      {
      CreateDSMmenu(subRC, &other[i].DSMom[j], &otherDSMpd[i]);
      InitializeDSMmenu(otherDSMpd[i], DSM, NULL);
      XtSetSensitive(other[i].DSMom[j], FALSE);


      name = XmStringCreateLocalized(other[i].title);
      n = 0;
      XtSetArg(args[n], XmNlabelString, name); ++n;
      other[i].toggleB[j] = XmCreateToggleButton(subRC, "otherTB", args, n);
      XtManageChild(other[i].toggleB[j]);

      XtAddCallback(other[i].toggleB[j], XmNvalueChangedCallback,
				(XtCallbackProc)SetOther, (XtPointer)(i<<8)+j);
      }
    }


  for (i = 0; asy[i].title; ++i)
    {
    n = 0;
    subFrame = XmCreateFrame(otherRC, "otherFrames", args, n);
    XtManageChild(subFrame);

    n = 0;
    subRC = XmCreateRowColumn(subFrame, "otherProbeRC", args, n);
    XtManageChild(subRC);

    name = XmStringCreateLocalized(asy[i].title);
    n = 0;
    XtSetArg(args[n], XmNlabelString, name); ++n;
    asy[i].toggleB[0] = XmCreateToggleButton(subRC, "otherTB", args, n);
    XtManageChild(asy[i].toggleB[0]);

    XtAddCallback(asy[i].toggleB[0], XmNvalueChangedCallback,
				(XtCallbackProc)SetAsync, (XtPointer)i);
    }

}	/* END INITOTHERPROBES */

/* -------------------------------------------------------------------- */
static void CreateDSMmenu(Widget parent, Widget *om, Widget *pd)
{
  int		n;
  Arg		args[2];

  n = 0;
  *pd = XmCreatePulldownMenu(parent, "DSMmenuPD", args, n);
	
  n = 0;
  XtSetArg(args[n], XmNsubMenuId, *pd); ++n;
  *om = XmCreateOptionMenu(parent, "DSMmenu", args, n);
  XtManageChild(*om);

}	/* END CREATEDSMMENU */

/* END XWIN.C */
