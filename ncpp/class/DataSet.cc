/*
-------------------------------------------------------------------------
OBJECT NAME:	DataSet.cc

FULL NAME:	Data Set Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-2000
-------------------------------------------------------------------------
*/

#include "DataSet.h"

#include <cfloat>
#include <algorithm>


/* -------------------------------------------------------------------- */
DataSet::DataSet(DataFile *df, Probe *prb, FlightClock& start, int nRecs, DataType dt, NormType nt) : file(df), probe(prb), startTime(start)
{
  int	i;

  accum = NULL;
  conc = surface = volume = NULL;

  computeConc = False;

  nRecords = nRecs;
  nWords = probe->DataRate() * probe->VectorLength() * nRecs;
  SetDataTypes(dt);

  for (i = 0; i < 256; ++i)
    normalization[i] = 1.0;

  for (i = 0; i < probe->nOtherVars(); ++i)
    otherVars[i] = new float[nRecs];

  SetNormalize(nt);

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void DataSet::SetDataTypes(DataType dt)
{
  if (dt & COUNTS || computeConc) {
    if (!accum)
      accum = new float[nWords];
    }
  else
    if (accum) {
      delete [] accum;
      accum = NULL;
      }

  if (probe->HaveConcentrations() && dt & (CONCENTRATION | SURFACE | VOLUME)) {
    if (!conc)
      conc = new float[nWords];
    }
  else
    if (conc) {
      delete [] conc;
      conc = NULL;
      }

  if (probe->HaveConcentrations() && dt & SURFACE) {
    if (!surface)
      surface = new float[nWords];
    }
  else
    if (surface) {
      delete [] surface;
      surface = NULL;
      }

  if (probe->HaveConcentrations() && dt & VOLUME) {
    if (!volume)
      volume = new float[nWords];
    }
  else
    if (volume) {
      delete [] volume;
      volume = NULL;
      }

}	/* END SETDATATYPE */

/* -------------------------------------------------------------------- */
void DataSet::SetNormalize(NormType nt)
{
  normType = nt;

  for (int i = 1; i < probe->VectorLength(); ++i)
    {
    switch (normType)
      {
      case LINEAR:
        normalization[i] = probe->BinWidth(i);
        break;

      case LOG:
        normalization[i] = log10(probe->CellSize(i)) - log10(probe->CellSize(i-1));
        break;

      default:
        normalization[i] = 1.0;
      }
    }

  findMinMax();

}	/* END SETNORMALIZE */

/* -------------------------------------------------------------------- */
void DataSet::SetCompute(bool x)
{
  computeConc = x;

  if (computeConc && !accum)
      accum = new float[nWords];

}	/* END SETCOMPUTE */

/* -------------------------------------------------------------------- */
void DataSet::ResizeData(int nRecs)
{
  int	i;

  nRecords = nRecs;
  nWords = probe->DataRate() * probe->VectorLength() * nRecs;

  if (accum)
    {
    delete [] accum;
    accum = new float[nWords];
    }

  if (conc)
    {
    delete [] conc;
    conc = new float[nWords];
    }

  if (surface)
    {
    delete [] surface;
    surface = new float[nWords];
    }

  if (volume)
    {
    delete [] volume;
    volume = new float[nWords];
    }

  for (i = 0; i < probe->nOtherVars(); ++i)
    {
    delete [] otherVars[i];
    otherVars[i] = new float[nRecs];
    }

}	/* END RESIZEDATA */

/* -------------------------------------------------------------------- */
void DataSet::ReadData(int nRecs, int avRate)
{
  int	i, j, k;
  long	startV[3], countV[3], nPoints;
  float	*accumBuff = NULL;
  float	*concBuff = NULL;
  float	*timeSeriesData[MAX_O_VARS];

  nRecords = nRecs;

  if (probe->DataRate() > 1)
    avRate = 1;


// Setup for reading counts and/or concentrations.
  startV[0] = startTime - file->StartTime();
  startV[1] = startV[2] = 0;

  countV[0] = avRate;
  countV[1] = 1;
  countV[2] = probe->VectorLength();

  if (countV[1] == 0 || countV[2] == 0)
    {
    std::cerr << "Count[] = " << countV[0] << countV[1] << countV[2] << "\n";
    exit(1);
    }

  nPoints = countV[0] * countV[1] * countV[2];

/*
cout << "nRecs = " << nRecs << ", avRate = " << avRate << "\n";
cout << "Start[] = " << startV[0] << ", "<< startV[1]<<", "<< startV[2] << "\n";
cout << "Count[] = " << countV[0] << ", "<< countV[1]<<", "<< countV[2] << "\n";
*/
  if (accum)
    {
    accumBuff = new float[nPoints];
    memset(accum, 0, nRecs * probe->VectorLength() * sizeof(float));
    }

  if (conc)
    {
    concBuff = new float[nPoints];

    for (i = 0; i < nRecs * probe->VectorLength(); ++i)
      conc[i] = -32767.0;

//    memset(conc, 0, nRecs * probe->VectorLength() * sizeof(float));
    }

  if (surface)
    memset(surface, 0, nRecs * probe->VectorLength() * sizeof(float));

  if (volume)
    memset(volume, 0, nRecs * probe->VectorLength() * sizeof(float));

  for (i = 0; i < probe->nOtherVars(); ++i)
    timeSeriesData[i] = new float[avRate];


  for (i = 0; i < nRecs; ++i)
    {
    if (accum)
      probe->ReadCounts(startV, (const long *)countV, accumBuff);

    for (j = 0; j < probe->nOtherVars(); ++j)
      probe->ReadOtherVar(j, startV, countV, timeSeriesData[j]);

    if (conc)
      if (computeConc)
        probe->ComputeConcentration(accumBuff,concBuff, countV, timeSeriesData);
      else
        probe->ReadConcen(startV, (const long *)countV, concBuff);


    // Average other vars;
    for (j = 0; j < probe->nOtherVars(); ++j)
      {
      otherVars[j][i] = 0.0;

      for (k = 0; k < avRate; ++k)
        otherVars[j][i] += timeSeriesData[j][k];

      otherVars[j][i] /= avRate;

      if (strncmp(probe->OtherVarName(j), "FRNG", 4) == 0)
        probe->SetRange((int)otherVars[j][0]);
      }


    // Average data.
    for (j = probe->FirstBin(); j <= probe->LastBin(); ++j)
      {
      int dest = (i * probe->VectorLength()) + j, avCntr = 0;

      for (k = 0; k < avRate; ++k)
        {
        if (accum && accumBuff[(k * probe->VectorLength()) + j] != -32767.0)
          accum[dest] += accumBuff[(k * probe->VectorLength()) + j];

        if (conc && concBuff[(k * probe->VectorLength()) + j] != -32767.0)
          {
          if (conc[dest] == -32767.0)
            conc[dest] = concBuff[(k * probe->VectorLength()) + j];
          else
            conc[dest] += concBuff[(k * probe->VectorLength()) + j];

          ++avCntr;
          }
        }

      if (conc && avCntr > 0)
        conc[dest] /= avCntr;

// Convert 260X and 2D's to N/cm3.
if (conc && probe->Name().find("260X") != probe->Name().npos ||
    conc && probe->Name().find("1D") != probe->Name().npos ||
    conc && probe->Name().find("2D") != probe->Name().npos ||
    conc && probe->Name().find("HVPS") != probe->Name().npos)
  conc[dest] /= 1000;

      if (surface)
        surface[dest] = conc[dest] * 4.0 * M_PI *
		pow((probe->CellSize(j-1) + probe->CellSize(j)) / 4.0, 2.0);

      if (volume)
        volume[dest] = conc[dest] * 4.0 / 3.0 * M_PI *
		pow((probe->CellSize(j-1) + probe->CellSize(j)) / 4.0, 3.0);
      }

    if (probe->DataRate() > 1)
      {
      if (++startV[1] >= probe->DataRate())
        {
        startV[1] = 0;
        ++startV[0];
        }
      }
    else
      startV[0] += avRate;
    }


  if (accumBuff)
    delete [] accumBuff;

  if (concBuff)
    delete [] concBuff;

  for (i = 0; i < probe->nOtherVars(); ++i)
    delete [] timeSeriesData[i];

  findMinMax();

}	/* END READDATA */

/* -------------------------------------------------------------------- */
void DataSet::findMinMax()
{
  int	i, j;
  float	c;

  if (accum)
    {
    minAccum = FLT_MAX;
    maxAccum = -FLT_MAX;

    for (i = 0; i < nRecords; ++i)
      for (j = probe->FirstBin(); j <= probe->LastBin(); ++j)
        {
        c = Accumulation(i, j);

        minAccum = std::min(minAccum, c);
        maxAccum = std::max(maxAccum, c);
        }
    }

  if (conc)
    {
    minConc = FLT_MAX;
    maxConc = -FLT_MAX;

    for (i = 0; i < nRecords; ++i)
      for (j = probe->FirstBin(); j <= probe->LastBin(); ++j)
        {
        c = Concentration(i, j);

        if (c > 0.0)	// Smallest conc != 0.
          minConc = std::min(minConc, c);

        maxConc = std::max(maxConc, c);
        }

    if (maxConc == 0.0)
      minConc = 0.0;
    }

  if (surface)
    {
    minSurf = FLT_MAX;
    maxSurf = -FLT_MAX;

    for (i = 0; i < nRecords; ++i)
      for (j = probe->FirstBin(); j <= probe->LastBin(); ++j)
        {
        c = Surface(i, j);

        if (c > 0.0)	// Smallest surface != 0.
          minSurf = std::min(minSurf, c);
        maxSurf = std::max(maxSurf, c);
        }

    if (maxSurf == 0.0)
      minSurf = 0.0;
    }

  if (volume)
    {
    minVol = FLT_MAX;
    maxVol = -FLT_MAX;

    for (i = 0; i < nRecords; ++i)
      for (j = probe->FirstBin(); j <= probe->LastBin(); ++j)
        {
        c = Volume(i, j);

        if (c > 0.0)	// Smallest vol != 0.
          minVol = std::min(minVol, c);
        maxVol = std::max(maxVol, c);
        }

    if (maxVol == 0.0)
      minVol = 0.0;
    }

}	/* END FINDMINMAX */

/* -------------------------------------------------------------------- */
DataSet::~DataSet()
{
  if (accum)	delete [] accum;
  if (conc)	delete [] conc;
  if (surface)	delete [] surface;
  if (volume)	delete [] volume;

}	/* END DESTRUCTOR */

/* END DATASET.CC */
