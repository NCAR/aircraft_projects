/*
-------------------------------------------------------------------------
OBJECT NAME:	DataFile.h

FULL NAME:	Data File Class

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef DATAFILE_H
#define DATAFILE_H

#include "define.h"

#include "fssp.h"
#include "s100.h"
#include "s200.h"
#include "f300.h"
#include "pcasp.h"
#include "x260.h"
#include "x200.h"
#include "y200.h"
#include "2D_P.h"
#include "2D_C.h"
#include "hvps.h"

#include "Time.h"


/* -------------------------------------------------------------------- */
class DataFile {

public:
	DataFile(char fName[]);
	~DataFile();

  const std::string&	FileName() const	{ return(fileName); }
  const std::string&	ProjectName() const	{ return(projName); }
  const std::string&	FlightNumber() const	{ return(flightNum); }
  const std::string&	FlightDate() const	{ return(flightDate); }

  FlightClock	StartTime()	const	{ return(startTime); }
  FlightClock	EndTime()	const	{ return(endTime); }

  int	NumberOfProbes() const	{ return(nProbes); }

  bool  operator==(DataFile& rhs) { return(fileName == rhs.fileName); }
  bool  operator==(const DataFile& rhs) { return(fileName == rhs.fileName); }

  Probe		*probe[MAX_PROBES];


private:
  NcFile	*file;

  std::string	fileName;
  std::string	projName, flightNum, flightDate;

  int	nProbes;

  int	baseDataRate;

  FlightClock	startTime, endTime;

  bool	validProbeName(const char target[]) const;

};	/* END DATAFILE.H */

#endif
