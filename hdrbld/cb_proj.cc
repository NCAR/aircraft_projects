#include "hdrbld.h"
#include "pms.h"
#include "vardb.h"
#include <unistd.h>

#include <Xm/TextF.h>

/* -------------------------------------------------------------------- */
void SetProject(Widget w, XtPointer client, XtPointer call)
{
  char		*p;
  int		pn;

  p = XmTextFieldGetString(projText[0]);
  pn = atoi(p);
  XtFree(p);

  if (pn == 0)
    ProjectNumber = "defaults";

  sprintf(flightInfo.prnum, "%d", pn);
  XmTextFieldSetString(projText[0], flightInfo.prnum);
  ProjectNumber = flightInfo.prnum;

printf("SetProject: new proj# = %s\n", flightInfo.prnum);

  ReleaseVarDB();
  ReleasePMSspecs();

  sprintf(buffer, "%s/%s", ProjectDirectory, ProjectNumber);

  if (access(buffer, R_OK) == (-1))
    {
    fprintf(stderr, "Can't open %s for reading, does project exist?\n", buffer);
    return;
    }
printf(">>>>SetProj needs work still.\n");
//return;
  sprintf(buffer, "%s/%s/PMSspecs", ProjectDirectory, ProjectNumber);
  InitPMSspecs(buffer);

  sprintf(buffer, "%s/%s/VarDB", ProjectDirectory, ProjectNumber);
  InitializeVarDB(buffer);

}

/* END SETSH.C */
