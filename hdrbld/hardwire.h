/*
 * This file contains variables that are currently hardwired and should be
 * removed as time allows.
 */

#include <Xm/Xm.h>
#include "constants.h"
#undef NULL

struct bb
	{
	char	*blockType;
	void	(*initFn)(Widget);
	} ;

struct standard
	{
	char	*title;
	char	*blkName;
	int	blk_len;

	Widget	toggleB[2], DSMom[2];
	int	rate;
	} ;

struct projF
	{
	char	*fileName;
	void	(*cb)(Widget, XtPointer, XtPointer);
	} ;

struct nav
	{
	char	*longName;
	char	*blkName;
	int	blk_len;
	} ;

struct pmsLocns
	{
	char	*title;
	char	*abbrev;
	bool	enabled; /* Is this location valid for the given Aircraft */
	int	type;		/* 0 = None, 1 = PMS 1d, 2 = PMS 2d	*/

	/*	rowCol menu   menu   menu          menu	*/
	Widget	rc, probe, DSMom, interfaceNum, channelNum;
	} ;

extern char *typeList[];
extern char *typeListChar[];
extern char *sampleRates[];
extern char *gains[];
extern char *offsets[];
extern char *gpsLocns[], *irsLocns[];
extern char *twoDresolutions[];


extern struct bb	blockButtons[];
extern struct nav	inertial[], gps[];
extern struct pmsLocns	pmsInfo[];
extern struct standard	other[], asy[];
extern struct projF	projectFiles[];
extern char		*eventLocns[];
