/*
-------------------------------------------------------------------------
OBJECT NAME:	hdrbld.h

DESCRIPTION:	Main header file for hdrbld.c
-------------------------------------------------------------------------
*/

#ifndef HDRBLD_H
#define HDRBLD_H

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <sys/types.h>
#include <Xm/Xm.h>

#include "constants.h"
#undef NULL
#include "header.h"

#define NAMELEN			NAMLEN
#define MAX_NAV			5
#define MAX_PMS			50
#define MAX_LOCN		16
#define MAX_DSM			6
#define MAX_OTHER		12

#define HEADER		"%s/%s/header"

/* Global Variables	*/
extern char		buffer[], *aircraft[], FileName[], *DSM[];
extern char		*ProjectDirectory, *ProjectNumber, ProjectName[];
extern int		nsdi, nPMS;
extern int		Inertial[], GPS[];
extern bool		ChangesMade;
extern struct Sh	*sdi[];
extern struct Sh	currentSh;
extern struct Fl	flightInfo;

extern Widget  projText[];
 
extern Widget
	varText, SDIom[], calText[], acButts[], acOpMenu,
	varList, sdiFrame, sdiDSMbutts[], typeButts[], srButts[],
        cardAddrButts[], gainButts[], offsetButts[],
        blockButtonFrame, blockFrame[],
        navDSMom[], navTypeOM[], pmsTypeOM[], pmsDSMom[], otherDSMom[];



/*      Function Prototypes
 */
FILE	*OpenProjectFile(char filename[], char mode[], int action);

int	AccessProjectFile(char filename[], char mode[]),
	LocatePMSlocn(char locn[]);

char	*SearchList(char **list, char target[]),
	*GetMenu(Widget);

void	SortTable(char **table, int beg, int end),
	SetMenu(Widget, char target[]),
	PreWidgetInitialize(), PostWidgetInitialize(),
	ProcessArgv(int argc, char **argv),
	SetDSMlist(char s[]), SetPMSlocns(char s[]),
	FillListWidget(), SortSh(),
	InitializeDSMmenu(Widget parent, char *dsmList[], void (*cb)()),
	LogMessage(char msg[]), AddToChangeLog(char msg[]);

void	HandleError(), HandleWarning();


void
	OpenNewFile(Widget w, XtPointer client, XtPointer call),
	OpenNewFile_OK(Widget w, XtPointer client, XmFileSelectionBoxCallbackStruct
	*call),
	SaveFileAs(Widget w, XtPointer client, XtPointer call),
	SaveFileAs_OK(Widget w, XtPointer client, XmFileSelectionBoxCallbackStruct *
call),
	SaveFile(Widget w, XtPointer client, XtPointer call),
	EditVariable(Widget w, XtPointer client, XmListCallbackStruct *call),
	Accept(Widget w, XtPointer client, XtPointer call),
	Clear(Widget w, XtPointer client, XtPointer call),
	Delete(Widget w, XtPointer client, XtPointer call),
	EditSDI(Widget w, XtPointer client, XtPointer call),
	ShowBlock(Widget w, XtPointer client, XtPointer call),
	EditBlocks(Widget w, XtPointer client, XtPointer call),
	EditProjectFile(Widget w, XtPointer client, XtPointer call),
	EditDefaultFile(Widget w, XtPointer client, XtPointer call),
	EditHostsFile(Widget w, XtPointer client, XtPointer call),
	EditVarDB(Widget w, XtPointer client, XtPointer call),
	HeaderDump(Widget w, XtPointer client, XtPointer call),
	forkXterm(Widget w, XtPointer client, XtPointer call),
	forkXterm4xfer(Widget w, XtPointer client, XtPointer call),
	ValidateVarName(Widget w, XtPointer client, XtPointer call),
	MapCalCof(Widget w, XtPointer client, XtPointer call),
	Print(Widget w, XtPointer client, XtPointer call),
	Search(Widget w, XtPointer client, XtPointer call),
	CreateProject(Widget w, XtPointer client, XtPointer call),
	SaveQuit(Widget w, XtPointer client, XtPointer call),
	Quit(Widget w, XtPointer client, XtPointer call);
 
void
	SetAircraft(Widget w, XtPointer client, XtPointer call),
	SetProject(Widget w, XtPointer client, XtPointer call),
	SetSDI_DSM(Widget w, XtPointer client, XtPointer call),
	SetSDI_Type(Widget w, XtPointer client, XtPointer call),
	SetSDI_SampleRate(Widget w, XtPointer client, XtPointer call),
	SetSDI_CardAddr(Widget w, XtPointer client, XtPointer call),
	SetSDI_Gain(Widget w, XtPointer client, XtPointer call),
	SetSDI_Offset(Widget w, XtPointer client, XtPointer call);

void
	SetPrimaryInertial(Widget w, XtPointer client, XtPointer call),
	SetSecondaryInertial(Widget w, XtPointer client, XtPointer call),
	SetPrimaryGPS(Widget w, XtPointer client, XtPointer call),
	SetSecondaryGPS(Widget w, XtPointer client, XtPointer call),
	SetTertiaryGPS(Widget w, XtPointer client, XtPointer call);

void	ClearCurrentSh(Widget w, XtPointer client, XtPointer call),
	SetPMS(Widget w, XtPointer client, XtPointer call),
	SetOther(Widget w, XtPointer client, XmToggleButtonCallbackStruct *call),
	SetAsync(Widget w, XtPointer client, XmToggleButtonCallbackStruct *call);

/* libraf declarations
 */
void *GetMemory(unsigned nbytes);
char *strupr(char s[]);

void	QueryFile(char *prompt, char *directory, void (*callBack)()),
	FileCancel(Widget w, XtPointer clientData, XtPointer callData),
	ExtractFileName(XmString str, char **text),
	CreateFileSelectionBox(Widget parent),
	ShowError(char str[]),
	ErrorOK(Widget w, XtPointer clientData, XtPointer callData),
	CreateErrorBox(Widget parent),
	WarnUser(char str[], void (*okCB)(), void (*cancelCB)()),
	CancelWarning(Widget w, XtPointer clientData, XtPointer callData),
	CreateWarningBox(Widget parent),
	QueryUser(char str[], int maxlen, void (*callBack)()),
	QueryCancel(Widget w, XtPointer clientData, XtPointer callData),
	CreateQueryBox(Widget parent),  ExtractAnswer(char *s);

#endif

/* END HDRBLD.H */
