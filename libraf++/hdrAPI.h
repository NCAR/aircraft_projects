/*
-------------------------------------------------------------------------
OBJECT NAME:	hdrAPI.h

DESCRIPTION:	Header file tape API package

COPYRIGHT:	University Corporation for Atmospheric Research, 1998
-------------------------------------------------------------------------
*/

#ifndef HDRAPI_H
#define HDRAPI_H

#ifndef NULL
#define NULL		(0)
#endif

#include "header.h"
#include "tapeIO.h"
#include "ntohf.h"

#include <string>
#include <sys/types.h>
#include <netinet/in.h>


/* -------------------------------------------------------------------- */
class Header
{
public:
	Header(const char fName[]);
	Header(const std::string fName);
	Header(TapeDrive &drv);	// tapes are slow, provide access
				// for already open drive.
	~Header();

  void 	readHeader(const char fName[]);

  void 	*HeaderPointer()	{ return((void *)header); }

  char	*ProjectName();		// May not work if no PROJ_DIR

  // Struct Fl fields.
  char	*Version()		{ return(header->version); }
  char	*ProjectNumber()	{ return(header->prnum); }
  char	*FlightNumber()		{ return(header->fltnum); }
  char	*TapeNumber()		{ return(header->tpnum); }
  char	*FlightDate()		{ return(header->date); }
  char	*FlightTime()		{ return(header->time); }
  char	*TimeZone()		{ return(header->tzone); }
  char	*Aircraft()		{ return(header->acraft); }

  long	NumberItems()		{ return(ntohl(header->n_items)); }
  long	lrLength()		{ return(ntohl(header->lrlen)); }
  long	lrPpr()			{ return(ntohl(header->lrppr)); }
  long	HeaderLength()		{ return(ntohl(header->thdrlen)); }

  char	*ADStype()		{ return(header->ads_type); }


  void	*GetFirst(), *GetFirst(char blkName[]), *GetSDI(char varName[]);
  void	*GetNext(), *GetNext(char blkName[]);


  char	*ItemType(void *vp)	{ return(((Blk *)vp)->item_type); }
  long	ItemLength(void *vp)	{ return(ntohl(((Blk *)vp)->item_len)); }
  long	Start(void *vp)		{ return(ntohl(((Blk *)vp)->start)); }
  long	SizeOf(void *vp)	{ return(ntohl(((Blk *)vp)->length)); }

  long	SampleRate(Dme *vp)	{ return(ntohl(vp->rate)); }
  long	SampleRate(Ins *vp)	{ return(ntohl(vp->rate)); }
  long	SampleRate(Masp *vp)	{ return(ntohl(vp->rate)); }
  long	SampleRate(Pms1 *vp)	{ return(ntohl(vp->rate)); }
  long	SampleRate(Pms1v2 *vp)	{ return(ntohl(vp->rate)); }
  long	SampleRate(Serial *vp)	{ return(ntohl(vp->rate)); }
  long	SampleRate(Sh *vp)	{ return(ntohl(vp->rate)); }

  // Which DSM is probe/sensor attached to.
  char	*DSM(Asy *vp)		{ return(vp->dsm_locn); }
  char	*DSM(Blk *vp)		{ return(vp->dsm_locn); }
  char	*DSM(Dme *vp)		{ return(vp->dsm_locn); }
  char	*DSM(Evt *vp)		{ return(vp->dsm_locn); }
  char	*DSM(Ins *vp)		{ return(vp->dsm_locn); }
  char	*DSM(Irs *vp)		{ return(vp->dsm_locn); }
  char	*DSM(Masp *vp)		{ return(vp->dsm_locn); }
  char	*DSM(Pms1 *vp)		{ return(vp->dsm_locn); }
  char	*DSM(Pms1v2 *vp)	{ return(vp->dsm_locn); }
  char	*DSM(Pms2 *vp)		{ return(vp->dsm_locn); }
  char	*DSM(Pms2h *vp)		{ return(vp->dsm_locn); }
  char	*DSM(Serial *vp)	{ return(vp->dsm_locn); }
  char	*DSM(Sh *vp)		{ return(vp->dsm_locn); }
  char	*DSM(Uvhyg *vp)		{ return(vp->dsm_locn); }

  // Probe/sensor mounting location.
  char	*AircraftLocation(Blk *vp)	{ return(vp->locn); }
  char	*AircraftLocation(Evt *vp)	{ return(vp->locn); }
  char	*AircraftLocation(Irs *vp)	{ return(vp->locn); }
  char	*AircraftLocation(Masp *vp)	{ return(vp->locn); }
  char	*AircraftLocation(Pms1 *vp)	{ return(vp->locn); }
  char	*AircraftLocation(Pms1v2 *vp)	{ return(vp->locn); }
  char	*AircraftLocation(Pms2 *vp)	{ return(vp->locn); }
  char	*AircraftLocation(Pms2h *vp)	{ return(vp->locn); }
  char	*AircraftLocation(Uvhyg *vp)	{ return(vp->locn); }


  // Struct Sh (SDI or Analog/Digital stuff).
  long	DSMaddress(Sh *vp)		{ return(ntohl(vp->adsaddr)); }
  char	*SDItype(Sh *vp)		{ return(vp->type); }
  long	InterleaveOffset(Sh *vp)	{ return(ntohl(vp->offset)); }

  float	AtoDconversionFactor(Sh *vp)	{ return(ntohf(vp->convert)); }
  long  AtoDconversionOffset(Sh *vp)	{ return(ntohl(vp->convert_offset)); }

  long  ChannelGain(Sh *vp)	{ return(ntohl(vp->ch_gain)); }
  long  ChannelOffset(Sh *vp)	{ return(ntohl(vp->ch_offset)); }


  char	*VariableName(Asy *vp)		{ return(vp->name); }
  char	*VariableName(Masp *vp)		{ return(vp->item_type); }
  char	*VariableName(Pms1 *vp)		{ return(vp->name); }
  char	*VariableName(Pms1v2 *vp)	{ return(vp->name); }
  char	*VariableName(Pms2 *vp)		{ return(vp->name); }
  char	*VariableName(Pms2h *vp)	{ return(vp->name); }
  char	*VariableName(Serial *vp)	{ return(vp->name); }
  char	*VariableName(Sh *vp)		{ return(vp->name); }

  long	CalibrationOrder(Sh *vp)	{ return(ntohl(vp->order)); }
  float	CalibrationCoefficient(Sh *vp, int i)	{ return(ntohf(vp->cof[i])); }

  char	*SerialNumber(Masp *vp)		{ return(vp->serial_num); }
  char	*SerialNumber(Pms1v2 *vp)	{ return(vp->serial_num); }
  char	*SerialNumber(Pms2 *vp)		{ return(vp->serial_num); }
  char	*SerialNumber(Pms2h *vp)	{ return(vp->serial_num); }
  char	*SerialNumber(Uvhyg *vp)	{ return(vp->serial_num); }

  long	InterfaceNumber(Pms1v2 *vp)	{ return(ntohl(vp->intf_num)); }
  long	InterfaceChannel(Pms1v2 *vp)	{ return(ntohl(vp->intf_chan)); }
  long	InterfaceChannel(Pms2 *vp)	{ return(ntohl(vp->intf_chan)); }

  long	ParticleSpacingStart(Pms1v2 *vp)  { return(ntohl(vp->ps_start)); }
  long	ParticleSpacingLength(Pms1v2 *vp) { return(ntohl(vp->ps_length)); }
  float	ParticleSpacingGate(Pms1v2 *vp)   { return(ntohf(vp->ps_gate)); }

  long	lrLength(Pms2 *vp)	{ return(ntohl(vp->lrlen)); }
  long	lrLength(Asy *vp)	{ return(ntohl(vp->lrlen)); }
  short	lrPpr(Pms2 *vp)		{ return(ntohs(vp->lrppr)); }
  long	lrPpr(Asy *vp)		{ return(ntohl(vp->lrppr)); }

  short	Resolution(Pms2 *vp)	{ return(ntohs(vp->resolution)); }


private:
  Fl	*header;
  char	*hdr;
  int	currentIndx;
  char	*currentPtr;

  char	projName[32];

};

#endif

/* END HDRAPI.H */
