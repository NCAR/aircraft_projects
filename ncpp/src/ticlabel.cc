/*
-------------------------------------------------------------------------
OBJECT NAME:	ticlabel.cc

FULL NAME:	Generate Various Types of Tic Mark Labels.

ENTRY POINTS:	MakeTimeTicLabel()
		MakeTicLabel()
		MakeLogTicLabel()

STATIC FNS:	none

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "define.h"

static char	label[32];

/* -------------------------------------------------------------------- */
std::string MakeTicLabel(float diff, int majorTics, double value)
{
  std::string	tmp;
  int		idiff = (int)diff;

  if (diff < 0.01)
    sprintf(label, "%f", value);
  else
  if (diff < 0.1)
    sprintf(label, "%.4f", value);
  else
  if (diff < 1.0)
    sprintf(label, "%.3f", value);
  else
  if (diff == (float)idiff && (idiff % majorTics) == 0)
    sprintf(label, "%ld", (long)value);
  else
  if (diff < 10.0)
    sprintf(label, "%.2f", value);
  else
  if (diff < 50.0)
    sprintf(label, "%.1f", value);
  else
    sprintf(label, "%ld", (long)value);

  tmp = label;

  return(tmp);

}	/* END MAKETICLABEL */

/* -------------------------------------------------------------------- */
std::string MakeLogTicLabel(double value)
{
  std::string	tmp;

  sprintf(label, "10^%d", (int)rint(log10(value)));
//  sprintf(label, "1.0E%+03d", value);

  tmp = label;

  return(tmp);
}

/* TICLABEL.CC */
