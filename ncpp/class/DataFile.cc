/*
-------------------------------------------------------------------------
OBJECT NAME:	DataFile.cc

FULL NAME:	netCDF Data File Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-2003
-------------------------------------------------------------------------
*/

#include "DataFile.h"
#include "netcdf.hh"

#include <unistd.h>

/* Put into config file. */

static const char *validProbeNames[] = {
	"AFSSP","AF300","APCAS","A260X","AASAS","A200X","A200Y","A300X",
	"AMASP","A1DC","A2DC","A1DP","A2DP","AS100","AS200","AS300",
	"ARDMA","ACLMT","ACMCA","AHVPS",NULL };


/* -------------------------------------------------------------------- */
DataFile::DataFile(char fName[]) : fileName(fName)
{
  int		i;
  NcAtt		*attr;
  NcVar		*avar, *cvar;

  nProbes = 0;

  /* Open Input File
   */
  file = new NcFile(fName);

  if (file->is_valid() == false)
    {
    sprintf(buffer, "Can't open %s.", fName);
    ErrorMsg(buffer);
    return;
    }

  attr = file->get_att("ProjectName");
  if (attr->is_valid())
    projName = attr->as_string(0);

  attr = file->get_att("FlightNumber");
  if (attr->is_valid())
    flightNum = attr->as_string(0);

  attr = file->get_att("FlightDate");
  if (attr->is_valid())
    flightDate = attr->as_string(0);

  attr = file->get_att("TimeInterval");
  if (attr->is_valid())
    {
    startTime = attr->as_string(0);
    endTime = strchr(attr->as_string(0), '-')+1;
    }


  // Bump up endTime if we have midnight roll-over.
  if (endTime < startTime)
    endTime += 86400;

  /* Scan variables for PMS1D vectors.
   */
  for (i = 2; i < file->num_vars(); ++i)
    {
    avar = file->get_var(i);

    if (avar->num_dims() >= 3 && validProbeName(avar->name()))
      {
      if (strncmp("AFSSP", avar->name(), 5) == 0)
        probe[nProbes++] = new FSSP(file, avar);
      else
      if (strncmp("AF300", avar->name(), 5) == 0 ||
          strncmp("AS300", avar->name(), 5) == 0)
        probe[nProbes++] = new F300(file, avar);
      else
      if (strncmp("AASAS", avar->name(), 5) == 0 ||
          strncmp("APCAS", avar->name(), 5) == 0)
        probe[nProbes++] = new PCASP(file, avar);
      else
      if (strncmp("AS100", avar->name(), 5) == 0)
        probe[nProbes++] = new S100(file, avar);
      else
      if (strncmp("AS200", avar->name(), 5) == 0)
        probe[nProbes++] = new S200(file, avar);
      else
      if (strncmp("A260X", avar->name(), 5) == 0)
        probe[nProbes++] = new X260(file, avar);
      else
      if (strncmp("AMASP", avar->name(), 5) == 0)
        probe[nProbes++] = new F300(file, avar);
      else
//      if (strncmp("AHVPS", avar->name(), 5) == 0)
//        probe[nProbes++] = new HVPS(file, avar);
//      else
      if (strncmp("A200X", avar->name(), 5) == 0)
        probe[nProbes++] = new X200(file, avar);
      else
      if (strncmp("A200Y", avar->name(), 5) == 0)
        probe[nProbes++] = new Y200(file, avar);
      else
      if (strncmp("A2DC", avar->name(), 4) == 0 ||
          strncmp("A1DC", avar->name(), 4) == 0)
        probe[nProbes++] = new TwoDC(file, avar);
      else
      if (strncmp("A2DP", avar->name(), 4) == 0 ||
          strncmp("A1DP", avar->name(), 4) == 0)
        probe[nProbes++] = new TwoDP(file, avar);
      else
        probe[nProbes++] = new Probe(file, avar);
      }
    }

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
DataFile::~DataFile()
{
  while (--nProbes >= 0)
    delete probe[nProbes];

printf("Warning: DataFile: Memory leak left in place to avoid netCDF bug.\n");
//  delete file;

}	/* END DESTRUCTOR */

/* -------------------------------------------------------------------- */
bool DataFile::validProbeName(const char target[]) const
{
  int	i;

  for (i = 0; validProbeNames[i]; ++i)
    if (strncmp(validProbeNames[i], target, strlen(validProbeNames[i])) == 0)
      return(true);

  return(false);

}	/* END VALIDPROBENAME */

/* END DATAFILE.CC */
