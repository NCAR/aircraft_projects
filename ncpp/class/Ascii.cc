/*
-------------------------------------------------------------------------
OBJECT NAME:	Ascii.cc

FULL NAME:	

ENTRY POINTS:	Update()

STATIC FNS:	

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-8
-------------------------------------------------------------------------
*/

#include "Ascii.h"

static char	*dashes = "        ---";

/* -------------------------------------------------------------------- */
Ascii::Ascii(const Widget parent) : TextWindow(parent, "ascii")
{

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void Ascii::Update(SetManager& sets, PlotManager *plotMgr)
{
  int	i, j;
  DataSet	*set;

  Clear();

  Append(plotMgr->Title().c_str()); Append(", ");
  Append(plotMgr->SubTitle().c_str()); Append("\n\n");

  for (set = sets.FirstSet(); set; set = sets.NextSet())
    {
    strcpy(buffer, set->probe->Name().c_str());
 
    strcat(buffer, "\n  Cell diameter end points (um)\n");

    for (i = 0; i < set->probe->VectorLength(); ++i)
      sprintf(&buffer[strlen(buffer)], "%11.3f", set->probe->CellSize(i));

    strcat(buffer, "\n");
    Append(buffer);
    buffer[0] = '\0';


    if (sets.DataTypes() & COUNTS)
      {
      strcat(buffer, "\n  Raw Counts\n");

      for (i = 0; i < sets.NumberRecords(); ++i)
        {
        for (j = 0; j < set->probe->VectorLength(); ++j)
          sprintf(&buffer[strlen(buffer)], "%11.0f", set->Accumulation(i, j));

        strcat(buffer, "\n");
        Append(buffer);
        buffer[0] = '\0';
        }
      }

    if (sets.DataTypes() & CONCENTRATION)
      {
      strcat(buffer, "\n  Concentrations dN");

      if (sets.GetNormalization() == LINEAR)
        strcat(buffer, "/dD (N/cm3/um)\n");
      else
      if (sets.GetNormalization() == LOG)
        strcat(buffer, "/dlogD (N/cm3)\n");
      else
        strcat(buffer, " (N/cm3)\n");

      for (i = 0; i < sets.NumberRecords(); ++i)
        {
        for (j = 0; j < set->probe->FirstBin(); ++j)
          strcat(buffer, dashes);

        for (; j <= set->probe->LastBin(); ++j)
          sprintf(&buffer[strlen(buffer)], "%11.3e", set->Concentration(i, j));

        for (; j < set->probe->VectorLength(); ++j)
          strcat(buffer, dashes);

        strcat(buffer, "\n");
        Append(buffer);
        buffer[0] = '\0';
        }
      }

    if (sets.DataTypes() & SURFACE)
      {
      strcat(buffer, "\n  Surface dS");

      if (sets.GetNormalization() == LINEAR)
        strcat(buffer, "/dD (um2/cm3/um)\n");
      else
      if (sets.GetNormalization() == LOG)
        strcat(buffer, "/dlogD (um2/cm3)\n");
      else
        strcat(buffer, " (um2/cm3)\n");

      for (i = 0; i < sets.NumberRecords(); ++i)
        {
        for (j = 0; j < set->probe->FirstBin(); ++j)
          strcat(buffer, dashes);

        for (; j <= set->probe->LastBin(); ++j)
          sprintf(&buffer[strlen(buffer)], "%11.3e", set->Surface(i, j));

        for (; j < set->probe->VectorLength(); ++j)
          strcat(buffer, dashes);

        strcat(buffer, "\n");
        Append(buffer);
        buffer[0] = '\0';
        }
      }

    if (sets.DataTypes() & VOLUME)
      {
      strcat(buffer, "\n  Volume dV");

      if (sets.GetNormalization() == LINEAR)
        strcat(buffer, "/dD (um3/cm3/um)\n");
      else
      if (sets.GetNormalization() == LOG)
        strcat(buffer, "/dlogD (um3/cm3)\n");
      else
        strcat(buffer, " (um3/cm3)\n");

      for (i = 0; i < sets.NumberRecords(); ++i)
        {
        for (j = 0; j < set->probe->FirstBin(); ++j)
          strcat(buffer, dashes);

        for (; j <= set->probe->LastBin(); ++j)
          sprintf(&buffer[strlen(buffer)], "%11.3e", set->Volume(i, j));

        for (; j < set->probe->VectorLength(); ++j)
          strcat(buffer, dashes);

        strcat(buffer, "\n");
        Append(buffer);
        buffer[0] = '\0';
        }
      }

    Append("\n");
    }

  MoveTo(0);

}	/* END UPDATE */

/* END ASCII.CC */
