/*
-------------------------------------------------------------------------
OBJECT NAME:	SetMgr.h

FULL NAME:	Data Set Manager

TYPE:		

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-2001
-------------------------------------------------------------------------
*/

#ifndef SETMGR_H
#define SETMGR_H

#include "define.h"

#include "DataSet.h"
#include "DataFile.h"
#include "Time.h"


/* -------------------------------------------------------------------- */
class SetManager {

public:
  friend void	AutoScaleAccum(SetManager&, Panel *),
		AutoScaleConc(SetManager&, Panel *),
		AutoScaleSurface(SetManager&, Panel *),
		AutoScaleVolume(SetManager&, Panel *);

	SetManager();

  void		Clear();

  int		NumberOfSets() const	{ return(numberSets); }

  int		AveragingRate() const		{ return(avRate); }
  void		SetAverageRate(int newRate);

  int		NumberRecords() const		{ return(nRecords); }
  void		SetNumberRecords(int newCnt);

  DataType	DataTypes() const		{ return(dataType); }
  void		SetDataTypes(DataType newDT);
  void		SetNormalize(NormType newN);
  NormType	GetNormalization()		{ return(normType); }
  void		SetCompute(bool x);

  void		SetStartTime(FlightClock start);

  bool		Add(DataFile *file, Probe *prb);
  void		Delete(DataFile *file, Probe *prb);

  DataSet	*FirstSet()
    { return(numberSets == 0 ? (DataSet *)NULL : set[currentSet = 0]); }

  DataSet	*NextSet()
    { return(++currentSet < numberSets ? set[currentSet] : (DataSet *)NULL); }


  void	ReadCurrentSet();
  void	ReadAllSets();

  void	PageForward();
  void	PageBackward();


private:
  int		avRate;		// Averaging rate.
  int		nRecords;	// Number records to display.
  DataType	dataType;
  NormType	normType;

  FlightClock	currentTime;	// StartTime to use for new data.

  int		numberSets;
  int		currentSet;

  DataSet	*set[MAX_DATASETS];

  float		minAccum, maxAccum, minBin, maxBin;
  float		minConc, maxConc, minCell, maxCell;
  float		minSurf, maxSurf, minVol, maxVol;

  void		findMinMax(), setEndTime(int idx);

};	/* END SETMGR.H */

#endif
