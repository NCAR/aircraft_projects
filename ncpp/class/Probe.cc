/*
-------------------------------------------------------------------------
OBJECT NAME:	Probe.cc

FULL NAME:	Probe Class

DESCRIPTION:	

INPUT:		

OUTPUT:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997-9
-------------------------------------------------------------------------
*/

#include "Probe.h"

#include <Xm/TextF.h>

static float	pcasDefSize[] =
        { 0.1, 0.12, 0.14, 0.17, 0.2, 0.25, 0.3, 0.4,
                0.5, 0.7, 0.9, 1.2, 1.5, 2.0, 2.5, 3.0 };

static float	f300DefSize[] =
        { 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7,
          0.8, 0.9, 1.0,                          // Step 0.1
          1.2, 1.4,                               // Step 0.2
          1.7, 2.0,                               // Step 0.3
          2.5, 3.0, 3.5, 4.0, 4.5, 5.0,           // Step 0.5
          6.0, 7.0, 8.0, 9.0, 10.0,               // Step 1.0
          12.0, 14.0, 16.0, 18.0, 20.0 };         // Step 2.0

static float	fsspDefSize[] =
        { 2.0, 5.0, 8.0, 11.0, 14.0, 17.0, 20.0, 23.0, 26.0,
           29.0, 32.0, 35.0, 38.0, 41.0, 44.0, 47.0,      // range 0
          2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0,
           20.0, 22.0, 24.0, 26.0, 28.0, 30.0, 32.0,      // range 1
          1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0,
           10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0,      // range 2
          0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5,
           5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0 };           // range 3


/* -------------------------------------------------------------------- */
Probe::Probe(NcFile *file, NcVar *av) : avar(av)
{
  std::string	tmp;
  int		i;
  char		*location;
  NcVar		*var;
  NcAtt		*attr;

  name = &avar->name()[1];

  tmp = "C"; tmp += name;
  cvar = file->get_var(tmp.c_str());

  if (cvar && !cvar->is_valid())
    cvar = NULL;

  if (cvar == NULL)
    std::cerr << "  Concentrations (" << tmp << ") not found.\n";


  if (name.find("260X") != name.npos)
    type = X260;
  else
  if (name.find("FSSP") != name.npos)
    type = FSSP;
  else
  if (name.find("F300") != name.npos)
    type = F300;
  else
  if (name.find("PCAS") != name.npos || name.find("ASAS") != name.npos)
    type = PCASP;
  else
  if (name.find("200X") != name.npos)
    type = X200;
  else
  if (name.find("200Y") != name.npos)
    type = Y200;
  else
  if (name.find("MASP") != name.npos)
    type = MASP;
  else
  if (name.find("300X") != name.npos)
    type = X300;
  else
  if (name.find("2DC") != name.npos || name.find("1DC") != name.npos)
    type = TWODC;
  else
  if (name.find("2DP") != name.npos || name.find("1DP") != name.npos)
    type = TWODP;
  else
  if (name.find("HVPS") != name.npos)
    type = HVPS;
  else
  if (name.find("S100") != name.npos)
    type = S100;
  else
  if (name.find("S200") != name.npos)
    type = S200;
  else
  if (name.find("S300") != name.npos)
    type = S300;
  else
  if (name.find("RDMA") != name.npos)
    type = RDMA;
  else
  if (name.find("CLMT") != name.npos)
    type = CLIMET;
  else
  if (name.find("MCA") != name.npos)
    type = CMCA;


  dataRate = avar->get_dim(1)->size();
  vectorLength = avar->get_dim(2)->size();

  units = avar->get_att("units")->as_string(0);

  if ((attr = avar->get_att("SerialNumber")))
    serialNum = attr->as_string(0);


  if ((attr = avar->get_att("FirstBin")))
    firstBin = attr->as_short(0);
  else
    firstBin = 1;

  if ((attr = avar->get_att("LastBin")))
    lastBin = attr->as_short(0);
  else
    lastBin = avar->get_dim(2)->size()-1;


  if ((attr = avar->get_att("CellSizes")))
    {
    for (i = 0; i < attr->num_vals(); ++i)
      diameter[i] = attr->as_float(i);
    }
  else
    {
    std::cout << "Cell diameters for " << name << " not present in file, using defaults.\n";
    sprintf(buffer, "Cell diameters for %s not present in file, using defaults.", name.c_str());

    ErrorMsg(buffer);

    if (type == X260)
      for (i = 0; i < 64; ++i)
        diameter[i] = 5 + i * 10;
    else
    if (type == X200)
      for (i = 0; i < 16; ++i)
        diameter[i] = 10 + i * 20;
    else
    if (type == Y200)
      for (i = 0; i < 16; ++i)
        diameter[i] = 150 + i * 300;
    else
    if (type == PCASP)
      for (i = 0; i < 16; ++i)
        diameter[i] = pcasDefSize[i];
    else
    if (type == F300)
      for (i = 0; i < 32; ++i)
        diameter[i] = f300DefSize[i];
    else
    if (type == FSSP)
      for (i = 0; i < 64; ++i)
        diameter[i] = fsspDefSize[i];
    else
    if (type == TWODC)
      for (i = 0; i < 64; ++i)
        diameter[i] = 17 + i * 25;
    else
    if (type == TWODP)
      for (i = 0; i < 64; ++i)
        diameter[i] = 145 + i * 200;
    else
    if (type == HVPS)
      for (i = 0; i < 256; ++i)
        diameter[i] = 145 + i * 200;
    }

  location = strchr(name.c_str(), '_');

  // Find associated houskeeping & derived variables (using location)
  for (i = 0, otherCnt = 0; i < file->num_vars(); ++i)
    {
    var = file->get_var(i);

    if (var->num_dims() < 3 &&
       (strstr(var->name(), location) && strncmp(var->name(), "EVENT_", 6)) ||
       strcmp(var->name(), "TASX") == 0)
      {
      otherVars[otherCnt++] = var;
      }
    }

  otherVars[otherCnt] = NULL;

  if (diameter[0] == 0.0)
    {
    std::cout << "Cell diameters for " << name <<
		" appear to be mid-point not end-point values.\n";
    std::cout << "  This will cause mildly erroneous/amusing results.\n";

    diameter[0] = diameter[1] - (diameter[2] - diameter[1]);
    }

  ComputeWidths();

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
bool Probe::ReadCounts(long start[], const long count[], float *data)
{
  if (avar == NULL)
    return(false);

  avar->set_cur(start);
  return(avar->get(data, count));

}	/* END READCOUNTS */

/* -------------------------------------------------------------------- */
bool Probe::ReadConcen(long start[], const long count[], float *data)
{
  if (cvar == NULL)
    return(false);

  cvar->set_cur(start);
  return(cvar->get(data, count));

}	/* END READCONCEN */

/* -------------------------------------------------------------------- */
void Probe::ComputeConcentration(float *accum, float *conc, long countV[],
	float *otherVarData[])
{
  std::cerr << "No Compute function at this time for " << cvar->name() << ".\n";

}	/* END COMPUTECONCENTRATION */

/* -------------------------------------------------------------------- */
bool Probe::ReadOtherVar(int idx, long start[], const long count[], float *data)
{
  if (otherVars[idx] == NULL)
    return(false);

  otherVars[idx]->set_cur(start);
  return(otherVars[idx]->get(data, count));

}	/* END READOTHERVAR */

/* -------------------------------------------------------------------- */
void Probe::UpdateCellDiams(const int first, const int last, const float *newDiams)
{
  int	nCells = type == FSSP ? 64 : VectorLength();

  firstBin = first;
  lastBin = last;

  for (int i = 0; i < nCells; ++i)
    diameter[i] = newDiams[i];

  ComputeWidths();

}	/* END UPDATECELLDIAMS */

/* -------------------------------------------------------------------- */
void Probe::ComputeWidths()
{
  int	nCells = type == FSSP ? 64 : VectorLength();

  midPointDiam[0] = binWidth[0] = 0.0;

  for (int i = 1; i < nCells; ++i)
    {
    midPointDiam[i] = (diameter[i] + diameter[i-1]) / 2;
    binWidth[i] = diameter[i] - diameter[i-1];
    }

}	/* END COMPUTEWIDTHS */

/* -------------------------------------------------------------------- */
int Probe::SetEditWindow(Widget txt[])
{
  int	nTxt, i, j, cnt;

  cnt = 0;

  sprintf(buffer, "%d", FirstBin());
  XmTextFieldSetString(txt[cnt++], buffer);

  sprintf(buffer, "%d", LastBin());
  XmTextFieldSetString(txt[cnt++], buffer);


  nTxt = VectorLength() / 16;
  if (Type() == FSSP)
    nTxt *= 4;

  for (i = 0; i < nTxt; ++i)
    {
    buffer[0] = '\0';

    for (j = 0; j < 16; ++j)
      sprintf(&buffer[strlen(buffer)], "%5g ", CellSize((i*16)+j));

    XmTextFieldSetString(txt[cnt++], buffer);
    }

  return(cnt);

}	/* END SETEDITWINDOW */

/* -------------------------------------------------------------------- */
int Probe::ApplyEditWindow(Widget text[])
{
  int	nTxt, i, j, cnt;
  float	cells[256];
  char	*p, *p1;

  cnt = 0;

  p = XmTextFieldGetString(text[cnt++]);
  i = atoi(p);
  if (i > 0 && i < VectorLength())
    firstBin = i;
  XtFree(p);

  p = XmTextFieldGetString(text[cnt++]);
  i = atoi(p);
  if (i > firstBin && i < VectorLength())
    lastBin = i;
  XtFree(p);


  nTxt = VectorLength() / 16;
  if (Type() == FSSP)
    nTxt *= 4;

  for (i = 0; i < nTxt; ++i)
    {
    p = XmTextFieldGetString(text[cnt++]);
    p1 = strtok(p, ", ");

    for (j = 0; j < 16; ++j)
      {
      cells[(i*16)+j] = atof(p1);
      p1 = strtok(NULL, ", ");
      }

    XtFree(p);
    }

  UpdateCellDiams(FirstBin(), LastBin(), cells);

  return(cnt);

}	/* END APPLYEDITWINDOW */

/* -------------------------------------------------------------------- */
Probe::~Probe() { }

/* END PROBE.CC */
