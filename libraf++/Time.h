/*
-------------------------------------------------------------------------
OBJECT NAME:	Time.h

FULL NAME:	Time Class

TYPE:		Concrete

DESCRIPTION:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1997
-------------------------------------------------------------------------
*/

#ifndef CLOCK_H
#define CLOCK_H

/* -------------------------------------------------------------------- */
class FlightClock {

public:
	FlightClock()		{ ssm = 0; label[0] = '\0'; }
	FlightClock(const int h, const int m, const int s);

  char		*c_str();
  int		Seconds() const	 { return(ssm); }   // Seconds since midnight

  void		SetTime(const int h, const int m, const int s);

  bool		operator!=(const FlightClock& rhs) { return(ssm != rhs.ssm); }
  bool		operator==(const FlightClock& rhs) { return(ssm == rhs.ssm); }
  bool		operator<=(const FlightClock& rhs) { return(ssm <= rhs.ssm); }
  bool		operator>=(const FlightClock& rhs) { return(ssm >= rhs.ssm); }
  bool		operator<(const FlightClock& rhs)  { return(ssm < rhs.ssm); }
  bool		operator>(const FlightClock& rhs)  { return(ssm > rhs.ssm); }

  bool		operator!=(const int rhs) { return(ssm != rhs); }
  bool		operator==(const int rhs) { return(ssm == rhs); }
  bool		operator<=(const int rhs) { return(ssm <= rhs); }
  bool		operator>=(const int rhs) { return(ssm >= rhs); }
  bool		operator<(const int rhs)  { return(ssm < rhs); }
  bool		operator>(const int rhs)  { return(ssm > rhs); }

  FlightClock&	operator=(const FlightClock& rhs);
  FlightClock&	operator=(const char rhs[]);
  FlightClock&	operator=(const int rhs);

  FlightClock&	operator++();		// prefix.
  FlightClock&	operator+=(const int rhs);
  FlightClock&	operator-=(const int rhs);
  FlightClock&	operator+=(const FlightClock& rhs);
  FlightClock&	operator-=(const FlightClock& rhs);

  int		operator-(const FlightClock& rhs) { return(ssm - rhs.ssm); }
  int		operator-(const int rhs)	  { return(ssm - rhs); }
  int		operator+(const FlightClock& rhs) { return(ssm + rhs.ssm); }
  int		operator+(const int rhs)	  { return(ssm + rhs); }
/*
  FlightClock&	operator-(const FlightClock& rhs);
  FlightClock&	operator-(const int rhs);
  FlightClock&	operator+(const FlightClock& rhs);
  FlightClock&	operator+(const int rhs);
*/

private:
  long	ssm;		// Seconds since midnight, this will not roll-over.
  char	label[10];

};	/* END CLOCK.H */

#endif
