/*
-------------------------------------------------------------------------
OBJECT NAME:	Time.cc

FULL NAME:	Generic Time Class

TYPE:		Concrete

ENTRY POINTS:	SetTime()

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#include "Time.h"
#include <cstdio>


/* -------------------------------------------------------------------- */
FlightClock::FlightClock(const int h, const int m, const int s)
{
  ssm = h * 3600 + m * 60 + s;

}	/* END CONSTRUCTOR */

/* -------------------------------------------------------------------- */
void FlightClock::SetTime(const int h, const int m, const int s)
{
  ssm = h * 3600 + m * 60 + s;

}	/* END SETTIME */

/* -------------------------------------------------------------------- */
FlightClock& FlightClock::operator=(const int s)
{
  ssm = s;

  return(*this);

}	/* END = */

/* -------------------------------------------------------------------- */
FlightClock& FlightClock::operator=(const FlightClock& rhs)
{
  if (this != &rhs)
    {
    ssm = rhs.ssm;
    }

  return(*this);

}	/* END = */

/* -------------------------------------------------------------------- */
FlightClock& FlightClock::operator=(const char rhs[])
{
  int	h, m, s;

  sscanf(rhs, "%d:%d:%d", &h, &m, &s);
  ssm = h * 3600 + m * 60 + s;

  return(*this);

}	/* END = */

/* -------------------------------------------------------------------- */
FlightClock& FlightClock::operator++() // prefix
{
  ++ssm;

  return(*this);

}	/* END ++ */

/* -------------------------------------------------------------------- */
FlightClock& FlightClock::operator+=(const int rhs)
{
  ssm += rhs;

  return(*this);

}	/* END += */

/* -------------------------------------------------------------------- */
FlightClock& FlightClock::operator-=(const int rhs)
{
  ssm -= rhs;

  return(*this);

}	/* END -= */

/* -------------------------------------------------------------------- */
FlightClock& FlightClock::operator+=(const FlightClock& rhs)
{
  ssm += rhs.ssm;
//  deconSSM(ssm);

  return(*this);

}	/* END += */

/* -------------------------------------------------------------------- */
FlightClock& FlightClock::operator-=(const FlightClock& rhs)
{
  ssm -= rhs.ssm;

  return(*this);

}	/* END -= */

/* -------------------------------------------------------------------- */
char *FlightClock::c_str()
{
  long	s = ssm;
  int	hour, min, sec;

  hour = s / 3600; s -= hour * 3600;
  min = s / 60; s -= min * 60;
  sec = s;

//  if (hour > 23)
//    hour -= 24;

  sprintf(label, "%02d:%02d:%02d", hour, min, sec);

  return(label);

}       /* END LABEL */

/* END TIME.CC */
