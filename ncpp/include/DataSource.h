/*
-------------------------------------------------------------------------
OBJECT NAME:	DataSource.h

FULL NAME:	Create File, Probe & Data type widgets

TYPE:		

DESCRIPTION:	This is a seperate class, because postage stamps & movie need
		seperate copies.

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef DATASOURCE_H
#define DATASOURCE_H

#include "define.h"


/* -------------------------------------------------------------------- */
class DataSource {

public:
  void	CreateDataSourceWidgets(const Widget, const Widget, const Widget,
	const Widget);
  void	SetFileNames();
  void	SetProbeNames();

  int	ActiveDataTypes();


protected:
  Widget	fileB[MAX_DATAFILES], probeB[MAX_PROBES], dataType[4];

};	/* END DATASOURCE.H */

#endif
