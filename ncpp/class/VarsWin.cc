/*
-------------------------------------------------------------------------
OBJECT NAME:	VarsWin.cc

FULL NAME:	

ENTRY POINTS:	Update()

STATIC FNS:	

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-8
-------------------------------------------------------------------------
*/

#include "VarsWin.h"

/* -------------------------------------------------------------------- */
VarsWin::VarsWin(const Widget parent) : TextWindow(parent, "vars")
{

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void VarsWin::Update(SetManager& sets, PlotManager *plotMgr)
{
  int	i, j;
  DataSet	*set;

  Clear();

  Append(plotMgr->Title().c_str()); Append(", ");
  Append(plotMgr->SubTitle().c_str()); Append("\n\n");

  for (set = sets.FirstSet(); set; set = sets.NextSet())
    {
    strcpy(buffer, set->probe->Name().c_str());
    strcat(buffer, "\n");

    for (i = 0; i < set->probe->nOtherVars(); ++i)
      {
      sprintf(&buffer[strlen(buffer)], "  %-12s", set->probe->OtherVarName(i));

      for (j = 0; j < sets.NumberRecords(); ++j)
        {
	sprintf(&buffer[strlen(buffer)], "%10.3f", set->OtherVar(i, j));
        }

      strcat(buffer, "\n");
      }

    strcat(buffer, "\n");
    Append(buffer);
    buffer[0] = '\0';
    }

  MoveTo(0);

}	/* END UPDATE */

/* END VARSWIN.CC */
