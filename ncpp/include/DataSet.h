/*
-------------------------------------------------------------------------
OBJECT NAME:	DataSet.h

FULL NAME:	Data set information

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef DATASET_H
#define DATASET_H

#include "define.h"

#include "DataFile.h"
#include "Probe.h"
#include "Time.h"


/* -------------------------------------------------------------------- */
class DataSet {

public:
	DataSet(DataFile *df, Probe *prb, FlightClock& start, int nRecs, DataType dt, NormType n);
	~DataSet();

  friend class SetManager;
  friend class Panel;		// RO access to plot data.

  FlightClock   StartTime()     const   { return(startTime); }
  FlightClock   EndTime()       const   { return(endTime); }

  void	SetDataTypes(DataType dt);
  void	SetNormalize(NormType nt);
  void	SetCompute(bool x);
  void	ResizeData(int nRecs);

  void	ReadData(int nRecs, int avRate);

  float	Accumulation(int s, int cell) const	
		{ return(accum[(s * probe->VectorLength()) + cell]); }

  float	Concentration(int s, int cell) const
    { return(conc[(s * probe->VectorLength()) + cell] / normalization[cell]); }

  float	Surface(int s, int cell) const
    { return(surface[(s * probe->VectorLength()) + cell] / normalization[cell]); }

  float	Volume(int s, int cell) const
    { return(volume[(s * probe->VectorLength()) + cell] / normalization[cell]); }

  float NormalizeFactor(int cell)	{ return(normalization[cell]); }

  float	OtherVar(int var, int idx)
		{ return(otherVars[var][idx]); }

  DataFile	*file;
  Probe		*probe;

private:
  int	nWords, nRecords;
  float	*accum, minAccum, maxAccum;
  float	*conc, minConc, maxConc;
  float	*surface, minSurf, maxSurf;
  float	*volume, minVol, maxVol;
  float	*otherVars[MAX_O_VARS];
  float	normalization[256];

  FlightClock	startTime, endTime;

  NormType	normType;

  void	findMinMax();

  bool computeConc;

};	/* END DATASET.H */

#endif
