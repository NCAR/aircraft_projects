/*
 * This file contains variables that are currently hardwired and should be
 * removed as time allows.
 */

#include "hdrbld.h"
#include "hardwire.h"


void	InitSDI(Widget), InitNavInstruments(Widget), InitPMSprobes(Widget),
	InitSerial(Widget), InitClimet(Widget), InitOtherProbes(Widget);

struct bb blockButtons[] =
	{
	{ "Analog/Digital",	InitSDI },
	{ "Navigation",		InitNavInstruments },
	{ "PMS",		InitPMSprobes },
	{ "Serial",		InitSerial },
	{ "Other",		InitOtherProbes },
	{ NULL,			NULL }
	};

/* SDI related stuff.
 */
char *typeList[] =
    { "Analog", "Digital 2", "Digital 8", "Digital 16", "Digital Out", "Counter", "Synchro", "Aux Analog", NULL };

char *typeListChar[] =
    { ANALOG_STR, "D2", "D8", "D16", DIGITAL_OUT_STR, COUNTER_STR, SYNCHRO_STR, ANALOG_AUX_STR, NULL };
 
 
char *sampleRates[] = { "1", "5", "25", "50", "55", "250", "1000", "5000", NULL };

char *gains[] = { "1", "2", "4", "10", "20", NULL };
char *offsets[] = { "0", "10", NULL };

char *twoDresolutions[] = { "25", "50", "100", "200", NULL };

/* Navigation related stuff.
 */
struct nav inertial[] =
	{
	{ "None",		"",		0 },
	{ "Hw LaserRef 3&4",	IRS_STR,	sizeof(Irs_blk) },
	{ "CMigits 3",		CMIGITS3_STR,	sizeof(Cmigits3_blk) },
	{ NULL,			NULL,		0 }
	};

char	*irsLocns[] =
	{ "INS1", "INS2" };

struct nav gps[] =
	{
	{ "None",		"",		0 },
	{ "Trimble TANS 2",	GPS_TANS2_STR,	sizeof(Gps_blk) },
	{ "Trimble TANS 3",	GPS_TANS3_STR,	sizeof(Gps_blk) },
	{ "Garmin WAHS",	GPS_GARMIN_STR,	sizeof(Garmin_blk) },
	{ "Collins (PPS)",	PPS_GPS_STR,	sizeof(Ppsgps_blk) },
	{ "Honeywell",		HW_GPS_STR,	sizeof(HwGps_blk) },
	{ NULL,			NULL,		0 }
	};

char	*gpsLocns[] =
	{ "PG", "SG1", "SG2" };


/* PMS related stuff.
 */
struct pmsLocns	pmsInfo[] =
	{
	{ "Left Wing Outboard ",	"LWO",	TRUE,	0, 0,0,0,0,0 },
	{ "Left Wing Inboard  ",	"LWI",	TRUE,	0, 0,0,0,0,0 },
	{ "Right Wing Outboard",	"RWO",	TRUE,	0, 0,0,0,0,0 },
	{ "Right Wing Inboard ",	"RWI",	TRUE,	0, 0,0,0,0,0 },
	{ "Window Left        ",	"WDL",	TRUE,	0, 0,0,0,0,0 },
	{ "Window Right       ",	"WDR",	TRUE,	0, 0,0,0,0,0 },
	{ "Left Pod Inboard   ",	"LPI",	TRUE,	0, 0,0,0,0,0 },
	{ "Left Pod Center    ",	"LPC",	TRUE,	0, 0,0,0,0,0 },
	{ "Left Pod Outboard  ",	"LPO",	TRUE,	0, 0,0,0,0,0 },
	{ "Right Pod Inboard  ",	"RPI",	TRUE,	0, 0,0,0,0,0 },
	{ "Right Pod Center   ",	"RPC",	TRUE,	0, 0,0,0,0,0 },
	{ "Right Pod Outboard ",	"RPO",	TRUE,	0, 0,0,0,0,0 },
	{ NULL,			NULL,	TRUE,	0, 0,0,0,0,0 }
	};


/* Event related stuff.
 */
char	*eventLocns[] = { "CKP", "FCL", "FCR", "RCL", "RCR", "CTL", NULL };


/* Async/Other Instruments.
 */
struct standard	other[] =
  {
  { "Digital Pressure    ",	DPRES_STR,	sizeof(Dpres_blk),
				{NULL, NULL}, {NULL, NULL}, 5 },
  { "OPHIR III           ",	OPHIR3_STR,	sizeof(Oph3_blk),
				{NULL, NULL}, {NULL, NULL}, 1 },
  { "UV Hygrometer       ",	UVHYG_STR,	sizeof(Uv_blk),
				{NULL, NULL}, {NULL, NULL}, 1 },
  { "h2o TDL             ",	H2OTDL_STR,	sizeof(Jpltdl_blk),
				{NULL, NULL}, {NULL, NULL}, 3 },
  { "Laser Hygrometer II ",	LHTDL_STR,	sizeof(LhTdl_blk),
				{NULL, NULL}, {NULL, NULL}, 1 },
  { "RDMA                ",	RDMA_STR,	sizeof(Rdma_blk),
				{NULL, NULL}, {NULL, NULL}, 1 },
  { "UWA Neph            ",	NEPH_STR,	sizeof(Neph_UW_blk),
				{NULL, NULL}, {NULL, NULL}, 1 },
  { "Nephelometer        ",	NEPH903_STR,	sizeof(Neph_blk),
				{NULL, NULL}, {NULL, NULL}, 1 },
  { "Climet              ",	CLIMET_STR,	sizeof(Climet_blk),
				{NULL, NULL}, {NULL, NULL}, 1 },
  { "  MCA              ",	MCA_STR,	sizeof(Mca_blk),
				{NULL, NULL}, {NULL, NULL}, 1 },
  { "NOAA/AOC ADC        ",	ADC_AOA_STR,	sizeof(AdcAoa_blk),
				{NULL, NULL}, {NULL, NULL}, 1 },
  { NULL,			NULL,		0,
				{NULL, NULL}, {NULL, NULL}, 1 }
  };

struct standard	asy[] =
  {
  { "Drop Sonde",	AVAPS_STR,	0, {NULL, NULL,}, {NULL, NULL} },
  { NULL,		NULL,		0, {NULL, NULL}, {NULL, NULL} }
  };


/* Edit Project Files Stuff.
 */
struct projF	projectFiles[] =
  {
  { "DependTable",	EditProjectFile },
  { "Defaults",		EditProjectFile },
  { "PMSspecs",		EditProjectFile },
  { "ascii_parms",	EditProjectFile },
  { "BcastVars",	EditProjectFile },
  { NULL,		NULL }
  } ;

/* END HARDWIRE.C */
