/*
-------------------------------------------------------------------------
OBJECT NAME:	process.cc

FULL NAME:	

ENTRY POINTS:	ProcessRecord()
		ProcessHVPSrecord()
		SetSampleArea()

STATIC FNS:	none

DESCRIPTION:	This is the 2d record processor, generates a queue of
		particles and computes all the derived parameters.
		There is a corresponding function in class/MainWindow.cc
		to actually draw the record and information.

INPUT:		

OUTPUT:		

REFERENCES:	

REFERENCED BY:	

NOTES:		

COPYRIGHT:	University Corporation for Atmospheric Research, 1999-2003
-------------------------------------------------------------------------
*/

#include "define.h"
#include "header.h"

#include "ControlWindow.h"

#include <sys/types.h>
#include <netinet/in.h>

#include <algorithm>

#define MAX_PROBES	4

static const float	TAS_COMPENSATE = 1.0;
static const int	lower_mask = 215, upper_mask = 40;

static float	sampleAreaC[128], sampleAreaP[128];

static struct recStats	output;

extern ControlWindow	*controlWindow;

struct recStats &ProcessHVPSrecord(P2d_rec *record, float version);
FILE *fout;


/* -------------------------------------------------------------------- */
struct recStats &ProcessRecord(P2d_rec *record, float version)
{
  int		i, j, thisTime, probeIdx, h, startTime, bin, nBins, overload;
  ulong		*p, slice, ppSlice, pSlice, syncWord, startMilliSec;
  bool		overloadAdded = false, debug = false;
  double	sampleVolume[128], diameter, z, conc, totalLiveTime;

  Particle	*cp;

  static P2d_hdr	prevHdr[MAX_PROBES];
  static ulong		prevTime[MAX_PROBES] = { 1,1,1,1 };
  static ulong		prevSlice[MAX_PROBES][2];

  if (((char *)&record->id)[0] == 'H')
    return(ProcessHVPSrecord(record, version));

  if (version < 3.35)
    syncWord = 0xff000000;
  else
    syncWord = 0x55000000;

  probeIdx = ((char *)&record->id)[1] - '1';
  if (((char *)&record->id)[0] == 'C')
    probeIdx += 2;


//if (record->msec == 397) debug = true; else debug = false;

  thisTime = (record->hour * 3600 + record->minute * 60 + record->second) * 1000 + record->msec; // in milliseconds

  if (version == -1)	// This means set time stamp only
  {
    prevTime[probeIdx] = thisTime;
    memcpy((char *)&prevHdr[probeIdx], (char *)record, sizeof(P2d_hdr));
    return(output);
  }

if (debug)
  printf("%02d:%02d:%02d.%d - ", record->hour, record->minute, record->second, record->msec);

  overload = prevHdr[probeIdx].overld;
  output.DASelapsedTime = thisTime - prevTime[probeIdx];
  output.tas = (float)record->tas * 125 / 255;

  totalLiveTime = 0.0;
  memset(output.accum, 0, sizeof(output.accum));

  switch (controlWindow->GetConcentration()) {
    case CENTER_IN:		nBins = 64; break;
    case RECONSTRUCTION:	nBins = 128; break;
    default:			nBins = 32;
    }


  // Compute frequency, which is used to convert timing words from TAS clock
  // pulses to milliseconds.  Most of sample volume is here, time comes in
  // later.
  if (((char *)&record->id)[0] == 'P')
    {
    output.resolution = 200;
    output.SampleVolume = 261.0 * 6.4;
    output.DOFsampleVolume = 0.0;

    for (i = 0; i < nBins; ++i)
      sampleVolume[i] = output.tas * sampleAreaP[i] * 0.001;
    }
  else
    {
    output.resolution = 25;
    output.SampleVolume = 61.0 * 0.8;
    output.DOFsampleVolume = 0.0;

    for (i = 0; i < nBins; ++i)
      sampleVolume[i] = output.tas * sampleAreaC[i] * 0.001;
    }


  output.frequency = output.resolution / output.tas;
  output.SampleVolume *= output.tas *
			(output.DASelapsedTime - record->overld) * 0.001;

  // Scan record, compute tBarElapsedtime and stats.
  p = (ulong *)record->data;
  ppSlice = prevSlice[probeIdx][0];
  pSlice = prevSlice[probeIdx][1];
  output.tBarElapsedtime = 0;
  output.nTimeBars = 0;
  output.nonRejectParticles = 0;
  output.minBar = 10000000;
  output.maxBar = 0;
  output.area = 0;

  startTime = prevTime[probeIdx] / 1000;
  startMilliSec = prevHdr[probeIdx].msec * 1000;

  // Loop through all slice in record.
  for (i = 0; i < 1024; ++i, ++p)
    {
    slice = *p;

    if (i > 515 && overloadAdded == false)
      {
      startMilliSec += overload * 1000;
      overloadAdded = true;
      }

    /* Have particle, will travel.
     */
if (debug) printf("%08x %08x %08x\n", ppSlice, pSlice, slice);
    if (slice == syncWord && ppSlice == 0xffffffff && pSlice != 0xffffffff)
      {
      cp = new Particle();
      cp->time = startTime;
      cp->msec = startMilliSec;

      cp->w = 1;        // first slice of particle is in sync word
      cp->h = 1;
      cp->area = 0;
      cp->edge = false;
      cp->reject = false;
      cp->timeReject = false;

      cp->timeWord = pSlice & 0x00ffffff;
      cp->deltaTime = (ulong)((float)cp->timeWord * output.frequency);
      output.minBar = std::min(output.minBar, cp->deltaTime);
      output.maxBar = std::max(output.maxBar, cp->deltaTime);

      if (!cp->timeReject)
        output.tBarElapsedtime += cp->deltaTime;

      ++output.nTimeBars;

      /* Determine height of particle.
       */
      ++p; ++i;
      for (; i < 1024 && *p != 0xffffffff; ++p, ++i)
        {
        ++cp->w;

        slice = ~(*p);

        /* Potential problem/bug with computing of x1, x2.  Works good if all
         * edge touches are contigious (water), not so good for snow, where
         * it will all get bunched up.  Counts total number of contacts for
         * each edge.
         */
        if (slice & 0x80000000) /* touched edge */
          {
          cp->edge |= 0xF0;
          cp->x1++;
          }

        if (slice & 0x00000001) /* touched edge */
          {
          cp->edge |= 0x0F;
          cp->x2++;
          }


        for (j = 0; j < 32; ++j, slice >>= 1)
          cp->area += slice & 0x0001;

        h = 32;
        for (   j = 0, slice = *p;
                j < 32 && (slice & 0x80000000); slice <<= 1, ++j)
          --h;
        for (   j = 0, slice = *p;
                j < 32 && (slice & 0x00000001); slice >>= 1, ++j)
          --h;

        cp->h = std::max(h, cp->h);
        }

      /* If the particle becomes rejected later, we need to now much time the
       * particle consumed, so we can add it to the deadTime, so sampleVolume
       * can be reduced accordingly.
       */
      cp->liveTime = (ulong)((float)(cp->w + 3) * output.frequency);

      cp->msec /= 1000;

if (debug)
  printf("%06x %d %d\n", cp->timeWord, cp->w, cp->h);

      if (controlWindow->RejectZeroAreaImage() && cp->w ==1 && cp->h == 1)
        {
//        printf("reject 0 area #%d\n", output.nTimeBars);
        cp->reject = true;
        }

      switch (controlWindow->GetConcentration())
        {
        case NONE:
          bin = std::max(cp->w, cp->h);
          break;

        case ENTIRE_IN:
          if (cp->edge)
            cp->reject = true;

          bin = cp->h;
          break;

        case CENTER_IN:
          if (cp->w > 121)
            {
            if (debug) printf("reject 121 rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }
          else
          if (cp->h < 24 && cp->w > 6 * cp->h)
            {
            if (debug) printf("reject 24 rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }
          else
          if (cp->h < 6 && cp->w > 3 * cp->h)
            {
            if (debug) printf("reject 6 rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }
          else
          if (cp->edge && cp->w >= cp->h * 2)
            {
            if (debug) printf("reject no-center rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }

          bin = std::max(cp->w, cp->h);
          break;

        case RECONSTRUCTION:
          if (cp->w > 121)
            {
            if (debug) printf("reject 121 rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }
          else
          if (cp->h < 24 && cp->w > 6 * cp->h)
            {
            if (debug) printf("reject 24 rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }
          else
          if (cp->h < 6 && cp->w > 3 * cp->h)
            {
            if (debug) printf("reject 6 rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }
          else
          if (cp->edge && (float)cp->h / cp->w < 0.2)
            {
            if (debug) printf("reject 20%% rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }

          if (!cp->edge || (cp->edge && cp->w / cp->h < 0.2))
            bin = std::max(cp->w, cp->h);
          else
          if (cp->edge && cp->edge != 0xffff) // One edge, but not both.
            bin = (int)((pow(cp->w >> 1, 2.0) + pow(cp->h, 2.0)) / cp->h);
          else
          if (cp->edge == 0xffff)
            bin = (int)sqrt(pow(cp->h + ((pow(cp->x2, 2.0) + pow(cp->x1, 2.0))
				/ 4 * cp->h), 2.0) + pow(cp->x1, 2.0));

          break;

        }

      if (!cp->reject && bin < 128)
        {
        output.accum[bin]++;
        output.area += cp->area;
        output.nonRejectParticles++;
        totalLiveTime += cp->liveTime + cp->deltaTime;
        }

      output.particles.EnQueue((void *)cp);

      startMilliSec += (cp->deltaTime + cp->liveTime);

      if (startMilliSec >= 1000000)
        {
        startMilliSec -= 1000000;
        ++startTime;
        }
      }

    ppSlice = pSlice;
    pSlice = slice;
    }

  if (output.nTimeBars > 0)
    output.meanBar = output.tBarElapsedtime / output.nTimeBars;

output.tBarElapsedtime += (ulong)(1024 * output.frequency);

  output.tBarElapsedtime /= 1000;	// convert to milliseconds
  output.frequency /= 1000;


  // Compute "science" data.
  totalLiveTime /= 1000000;	// convert to seconds
  output.concentration = output.lwc = output.dbz = z = 0.0;

  for (i = 1; i < nBins; ++i)
    {
    if (sampleVolume[i] > 0.0)
      {
      conc = output.accum[i] / (sampleVolume[i] * totalLiveTime);
      output.DOFsampleVolume += (sampleVolume[i] * totalLiveTime);
      }
    else
      conc = 0.0;

    diameter = i * output.resolution;
    output.lwc += conc * pow(diameter / 10, 3.0);
    z += conc * pow(diameter / 1000, 6.0);

    output.concentration += conc;
    }

  z /= 1000;
  output.lwc *= M_PI / 6.0 * 1.0e-6 * controlWindow->GetDensity();

  if (z > 0.0)
    output.dbz = 10.0 * log10(z * 1.0e6);
  else
    output.dbz = -100.0;

  // Save time for next round.
  prevTime[probeIdx] = thisTime;
  memcpy((char *)&prevHdr[probeIdx], (char *)record, sizeof(P2d_hdr));

  p = (ulong *)record->data;
  prevSlice[probeIdx][0] = p[1022];
  prevSlice[probeIdx][1] = p[1023];

  return(output);

}	/* END PROCESSRECORD */

/* -------------------------------------------------------------------- */
struct recStats &ProcessHVPSrecord(P2d_rec *record, float version)
{
  int		i, j, thisTime, probeIdx, h, startTime, bin, nBins,
		shaded, unshaded;
  ushort	*p, slice, ppSlice, pSlice, startMilliSec;
  bool		overloadAdded = false, debug = false;
  double	sampleVolume[512], diameter, z, conc, totalLiveTime;

  Particle	*cp;

  static P2d_hdr	prevHdr[MAX_PROBES];
  static ulong	prevTime[MAX_PROBES] = { 1,1,1,1 };
  static ushort	prevSlice[MAX_PROBES][2];

  probeIdx = ((char *)&record->id)[1] - '1';
  p = (ushort *)record->data;


  if (p[0] == 0xcaaa)
    {
    int		offset, cntr, toft;

    if (p[1] == 0xcaaa)
      offset = 0;
    else
      if (p[17] == 0x2043)
        offset = -1;
    else
      return(output);

/*
    for (i = 2 + offset; i < 18+offset; ++i)
      printf("%x ", p[i]);

    for (i = 28 + offset; i < 286+offset; ++i)
      printf("%x ");
    printf("\n");

printf("\n");

    for (i = 0, cntr = 0; i < 2048; ++i)
      {
      if (i < 286 && p[i] == 0x2043)
        toft = i;

      if (i > 286 && p[i] == 0x5555)
        ++cntr;
      }
  
    printf("fives cntr = %d 2043 @ %d\n", cntr, toft);
*/
    output.tas = -1.0;
    return(output);
    }


  thisTime = (record->hour * 3600 + record->minute * 60 + record->second) * 1000 + record->msec; // in milliseconds

  if (version == -1)	// This means set time stamp only
  {
    prevTime[probeIdx] = thisTime;
    memcpy((char *)&prevHdr[probeIdx], (char *)record, sizeof(P2d_hdr));
    return(output);
  }

if (debug)
  printf("%02d:%02d:%02d.%d - ", record->hour, record->minute, record->second, record->msec);

  output.DASelapsedTime = thisTime - prevTime[probeIdx];
  output.tas = (float)record->tas * 125 / 255;

  totalLiveTime = 0.0;
  memset(output.accum, 0, sizeof(output.accum));

  switch (controlWindow->GetConcentration()) {
    case CENTER_IN:		nBins = 512; break;
    default:			nBins = 256;
    }

  // Compute frequency, which is used to convert timing words from TAS clock
  // pulses to milliseconds.  Most of sample volume is here, time comes in
  // later.
  output.resolution = 200;
  output.SampleVolume = 203.0 * output.resolution * (256-80) * 1.0e-6;
  output.DOFsampleVolume = 0.0;

  output.frequency = output.resolution / output.tas;
  output.SampleVolume *= (output.tas * TAS_COMPENSATE) *
			(output.DASelapsedTime - record->overld);

  // Scan record, compute tBarElapsedtime and stats.
  p = (ushort *)record->data;
  ppSlice = prevSlice[probeIdx][0];
  pSlice = prevSlice[probeIdx][1];
  output.tBarElapsedtime = 0;
  output.nTimeBars = 0;
  output.nonRejectParticles = 0;
  output.minBar = 10000000;
  output.maxBar = 0;
  output.area = 0;

  startTime = prevTime[probeIdx] / 1000;
  startMilliSec = prevHdr[probeIdx].msec * 1000;

  // Loop through all slice in record.
  for (i = 0; i < 2048; ++i, ++p)
    {
    slice = *p;

    if (i > 515 && overloadAdded == false)
      {
      startMilliSec += record->overld * 1000;
      overloadAdded = true;
      }

    /* Have particle, will travel.  By locating a timing word.
     */
if (debug) printf("%08x %08x %08x\n", ppSlice, pSlice, p[0]);
    if (slice & 0x8000)
      {
      /* Reject particle if there are not two timing words.  Usually will happen
       * when start of particle crosses record boundaries.
       */
      if ((p[1] & 0x8000) != 0x8000)
        continue;

      cp = new Particle();
      cp->time = startTime;
      cp->msec = startMilliSec;

      cp->w = 0;        /* first slice of particle is in sync word */
      cp->h = 0;
      cp->area = 0;
      cp->edge = false;
      cp->reject = false;
      cp->timeReject = false;

//printf("timing words %x %x %x\n", p[-1], p[0], p[1]);

      cp->timeWord = (((ulong)p[0] << 14) & 0x0fffc000);
      cp->timeWord += (ulong)(p[1] & 0x3fff);
//printf("  time out = %x\n", cp->timeWord);
      cp->deltaTime = (ulong)((float)cp->timeWord * output.frequency);
      output.minBar = std::min(output.minBar, cp->deltaTime);
      output.maxBar = std::max(output.maxBar, cp->deltaTime);

      if (!cp->timeReject)
        output.tBarElapsedtime += cp->deltaTime;

      ++output.nTimeBars;
//printf("p[2] = %x\n", p[2]);

      /* Determine height of particle.
       */
      p += 2; i += 2;
      for (; i < 2048 && (*p & 0x8000) != 0x8000; ++p, ++i)
        {
        ++cp->w;
        slice = *p;

        unshaded = shaded = 0;

        if (slice == 0x4000)    // Starts in lower half of diode array.
          {
          ++p; ++i;
          slice = *p;

          unshaded = 128;
          }

        shaded = (slice & 0x3f80) >> 7;
        unshaded += slice & 0x007f;

//printf("  slice = %04x - %d %d\n", slice, unshaded, shaded);
        /* Loop through any additional words that make up this slice - e.g.
         * multiple particles in one array.
         */
        while ((p[1] & 0xc000) == 0)
          {
          ++p; ++i;
          slice = *p;

          shaded += (slice & 0x3f80) >> 7;
          shaded += slice & 0x007f;
//printf("        = %04x - %d %d\n", slice, unshaded, shaded);
          }



        /* Potential problem/bug with computing of x1, x2.  Works good if all
         * edge touches are contigious (water), not so good for snow, where
         * it will all get bunched up.  Counts total number of contacts for
         * each edge.
         */
        if (unshaded <= upper_mask) /* touched edge */
          {
          cp->edge |= 0xF0;
          cp->x1++;
          }

        if (shaded + unshaded >= lower_mask) /* touched lower edge (assuming 40 masked out) */
          {
          cp->edge |= 0x0F;
          cp->x2++;
          }

        cp->area += shaded * TAS_COMPENSATE;
        cp->h = std::max(cp->h, shaded);
        }

      --p; --i;


      /* If the particle becomes rejected later, we need to now much time the
       * particle consumed, so we can add it to the deadTime, so sampleVolume
       * can be reduced accordingly.
       */
      cp->liveTime = (ulong)((float)(cp->w) * output.frequency);
      cp->w *= TAS_COMPENSATE;

      cp->msec /= 1000;

if (debug)
  printf("%06x %d %d\n", cp->timeWord, cp->w, cp->h);

      if (controlWindow->RejectZeroAreaImage() && cp->w == 1 && cp->h == 1)
        {
//        printf("reject 0 area #%d\n", output.nTimeBars);
        cp->reject = true;
        }

      switch (controlWindow->GetConcentration())
        {
        case NONE:
          bin = std::max(cp->w, cp->h);
          break;

        case ENTIRE_IN:
          if (cp->edge)
            cp->reject = true;

          bin = cp->h;
          break;

        case CENTER_IN:
          if (cp->w > 121)
            {
            if (debug) printf("reject 121 rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }
          else
          if (cp->h < 24 && cp->w > 6 * cp->h)
            {
            if (debug) printf("reject 24 rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }
          else
          if (cp->h < 6 && cp->w > 3 * cp->h)
            {
            if (debug) printf("reject 6 rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }
          else
          if (cp->edge && cp->w >= cp->h * 2)
            {
            if (debug) printf("reject no-center rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }

          bin = std::max(cp->w, cp->h);
          break;

        case RECONSTRUCTION:
          if (cp->w > 121)
            {
            if (debug) printf("reject 121 rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }
          else
          if (cp->h < 24 && cp->w > 6 * cp->h)
            {
            if (debug) printf("reject 24 rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }
          else
          if (cp->h < 6 && cp->w > 3 * cp->h)
            {
            if (debug) printf("reject 6 rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }
          else
          if (cp->edge && (float)cp->h / cp->w < 0.2)
            {
            if (debug) printf("reject 20%% rule #%d\n", output.nTimeBars);
            cp->reject = true;
            }

          if (!cp->edge || (cp->edge && cp->w / cp->h < 0.2))
            bin = std::max(cp->w, cp->h);
          else
          if (cp->edge && cp->edge != 0xffff) // One edge, but not both.
            bin = (int)((pow(cp->w >> 1, 2.0) + pow(cp->h, 2.0)) / cp->h);
          else
          if (cp->edge == 0xffff)
            bin = (int)sqrt(pow(cp->h + ((pow(cp->x2, 2.0) + pow(cp->x1, 2.0))
				/ 4 * cp->h), 2.0) + pow(cp->x1, 2.0));
          break;
        }

      if (!cp->reject && bin < 1024)
        {
        output.accum[bin]++;
        output.area += cp->area;
        output.nonRejectParticles++;
        totalLiveTime += cp->liveTime + cp->deltaTime;
        }

      output.particles.EnQueue((void *)cp);

      startMilliSec += (cp->deltaTime + cp->liveTime);

      if (startMilliSec >= 1000000)
        {
        startMilliSec -= 1000000;
        ++startTime;
        }
      }

    ppSlice = pSlice;
    pSlice = slice;
    }

  if (output.nTimeBars > 0)
    output.meanBar = output.tBarElapsedtime / output.nTimeBars;

//output.tBarElapsedtime += (ulong)(2048 * output.frequency);

  output.tBarElapsedtime /= 1000;	// convert to milliseconds
  output.frequency /= 1000;


  // Compute "science" data.
  totalLiveTime /= 1000000;	// convert to seconds
  output.concentration = output.lwc = output.dbz = z = 0.0;

  for (i = 1; i < nBins; ++i)
    {
    if (output.SampleVolume > 0.0)
      {
      conc = output.accum[i] / (output.SampleVolume / 1000.0);
//      output.DOFsampleVolume += (output.SampleVolume * totalLiveTime);
      }
    else
      conc = 0.0;

//if (i < 30)printf("%d %d %f %f\n", i, output.accum[i], output.SampleVolume, totalLiveTime);

    diameter = i * output.resolution;
    output.lwc += conc * pow(diameter / 10, 3.0);
    z += conc * pow(diameter / 1000, 6.0);

    output.concentration += conc;
    }

//  output.concentration = output.nTimeBars / (output.SampleVolume / 1000.0);

  z /= 1000;
  output.lwc *= M_PI / 6.0 * 1.0e-6 * controlWindow->GetDensity();

  if (z > 0.0)
    output.dbz = 10.0 * log10(z * 1.0e6);
  else
    output.dbz = -100.0;

  // Save time for next round.
  prevTime[probeIdx] = thisTime;
  memcpy((char *)&prevHdr[probeIdx], (char *)record, sizeof(P2d_hdr));

  p = (ushort *)record->data;
  prevSlice[probeIdx][0] = p[2046];
  prevSlice[probeIdx][1] = p[2047];

  return(output);

}	/* END PROCESSHVPSRECORD */

/* -------------------------------------------------------------------- */
static float DOF2dP[] = { 0.0, 145.203, 261.0, 261.0, 261.0,
  261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0,
  261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0,
  261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0,
  261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0,
  261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0,
  261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0, 261.0 };

static float DOF2dC[] = { 0.0, 1.56, 6.25, 14.06, 25.0, 39.06, 56.25,
  61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0,
  61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0,
  61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0,
  61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0,
  61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0, 61.0,
  61.0, 61.0, 61.0 };

static float	diodeDiameter = 0.2;

void SetSampleArea()
{
  int	i;
  float	dia, eaw, dof;

  switch (controlWindow->GetConcentration())
    {
    case NONE:
      for (i = 1; i < 128; ++i)
        {
        sampleAreaC[i] = 61.0 * 0.8;
        sampleAreaP[i] = 261.0 * 6.4;
        }

      break;

    case ENTIRE_IN:
      for (i = 1; i <= 32; ++i)
        {
        sampleAreaC[i] = DOF2dC[i] * diodeDiameter * (32 - i - 1) / 8.0;
        sampleAreaP[i] = DOF2dP[i] * diodeDiameter * (32 - i - 1) / 1.0;
//printf("%d %f %f %e %e\n", i, (float)i*25, (float)i*200, sampleAreaC[i], sampleAreaP[i]);
        }

      break;

    case CENTER_IN:
      for (i = 1; i <= 64; ++i)
        {
        sampleAreaC[i] = DOF2dC[i] * 0.8;
        sampleAreaP[i] = DOF2dP[i] * 6.4;
//printf("%e %e\n", sampleAreaC[i], sampleAreaP[i]);
        }

      break;

    case RECONSTRUCTION:
      for (i = 1; i <= 128; ++i)
        {
        dia = (float)i * 25;
        eaw = ((32 * 25) + (2 * (dia / 2 - dia / 7.2414))) * 0.001;

        if (i < 60)
          dof = DOF2dC[i];
        else
          dof = DOF2dC[60];

        sampleAreaC[i] = dof * eaw;


        dia = (float)i * 200;
        eaw = ((32 * 200) + (2 * (dia / 2 - dia / 7.2414))) * 0.001;

        if (i < 60)
          dof = DOF2dP[i];
        else
          dof = DOF2dP[60];

        sampleAreaP[i] = dof * eaw;
//printf("%d %f %f %e %e %e %e\n", i, (float)i * 25, dia, DOF2dC[i] * 0.8, sampleAreaC[i], DOF2dP[i] * 6.4, sampleAreaP[i]);
        }

      break;
    }

}	/* END SETSAMPLEAREA */

/* END PROCESS */
