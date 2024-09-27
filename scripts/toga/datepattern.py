from datetime import datetime as _datetime
from calendar import timegm as _timegm
from time import strptime as _strptime

import logging

logger = logging.getLogger(__name__)

def timeFromPtime(text, pattern="%Y%m%d%H%M%S"):
    return _timegm(_strptime(text, pattern))


class Duration(object):
    """
    Associate time fields with a duration in seconds with the strftime
    format necessary to exactly represent a time to that resolution.  The
    duration is positive if the period is always exactly that long,
    otherwise the duration magnitude is the maximum length of the period.
    """

    def __init__(self, duration_seconds, sftime):
        """
        Create a Duration instance.

        duration_seconds is positive if the period is always exactly that
        long, allowing the start() and next() methods to use optimized
        algorithms.  If it is negative, then the duration is not exact, and
        the start() and next() methods will search for the next interval by
        advancing half the duration magnitude until the formatted time
        field changes.
        """
        self._period = duration_seconds
        self._sftime = sftime

    def period(self):
        return self._period

    def duration(self):
        return abs(self._period)

    def ftime_start(self):
        return self._sftime

    def formatTime(self, ttime):
        "Convert the given time to a string using the format."
        return _datetime.utcfromtimestamp(ttime).strftime(self._sftime)

    def start(self, ttime):
        "Return the start time for the period containing the given time."
        # Use the ftime for the period start to make the comparison.
        period = self._period
        if period > 0:
            tstart = ttime - (ttime % period)
        else:
            sstart = self.formatTime(ttime)
            tstart = _timegm(_strptime(sstart, self._sftime))
        return tstart

    def next(self, ttime):
        """
        Return the next start of the time period containing ttime.

        If the duration is exact, then it is just added to the period start
        time.  If not, the start period must be explicitly computed after
        advancing to a time in the next time period.
        """
        # This is not the most efficient approach, but at least it's robust.
        period = self._period
        if period > 0:
            tend = self.start(ttime)
            tend += period
        else:
            stime = self.formatTime(ttime)
            tend = ttime
            for i_ in xrange(3):
                tend -= period / 2
                if self.formatTime(tend) != stime:
                    break
            tend = self.start(tend)
        return tend


Year = Duration(-365*24*3600, "%Y")
Month = Duration(-32*24*3600, "%Y%m")
Day = Duration(24*3600, '%Y%m%d')
Hour = Duration(3600, '%Y%m%d%H')
Minute = Duration(60, '%Y%m%d%H%M')
Second = Duration(1, '%Y%m%d%H%M%S')

class DatePatternPeriod(object):

    def __init__(self, duration, wildcard, ftime):
        self._duration = duration
        self._wildcard = wildcard
        self._ftime = ftime

    def _formatTime(self, ttime, pattern=None):
        if not pattern:
            pattern = self._ftime
        return _datetime.utcfromtimestamp(ttime).strftime(pattern)

    def startPeriod(self, ttime):
        "Return the start time for the period containing the given time."
        return self._duration.start(ttime)

    def nextPeriod(self, ttime):
        "Return the next start of this time period."
        return self._duration.next(ttime)

    def duration(self):
        return self._duration.duration()

    def containedBy(self, begin, end):
        """
        Return True if the time range completely contains this period.
        """
        return bool(self.startPeriod(begin) == begin and
                    self.nextPeriod(begin) - 1 <= end)

    def wildcard(self, pattern):
        "Replace date pattern with wildcards for this time period."
        return pattern.replace(self._ftime, self._wildcard)


class GlobDatePeriods(object):
    """
    A set of DatePatternPeriod instances from year through seconds.

    This includes methods to replace periods with their glob wildcards.  It
    can be subclassed to use different wildcard schemes such as regular
    expressions and different strftime fields.
    """
    def __init__(self):
        self.year = DatePatternPeriod(Year, '[12][90][0-9][0-9]', '%Y')
        self.month = DatePatternPeriod(Month, '[01][0-9]', '%m')
        self.day = DatePatternPeriod(Day, '[0-3][0-9]', '%d')
        self.hour = DatePatternPeriod(Hour, '[0-2][0-9]', '%H')
        self.minute = DatePatternPeriod(Minute, '[0-5][0-9]', '%M')
        self.second = DatePatternPeriod(Second, '[0-5][0-9]', '%S')

    def getPeriods(self):
        "Return a list of the periods in order from year to second."
        return [self.year, self.month, self.day, 
                self.hour, self.minute, self.second]

    def wildcard(self, pattern, period):
        """
        Replace all lesser periods with wildcards, keeping the given period
        fixed.  So wildcard("%H%M%S", self.hour) replaces %M and %S.
        """
        periods = self.getPeriods()
        found = False
        for p in periods:
            if found:
                pattern = p.wildcard(pattern)
            if p == period:
                found = True
        return pattern


class DatePattern(object):
    """
    A strftime pattern which can match all times in a given time range.

    The strftime pattern is used to generate patterns which can match all
    the times in an arbitrary range of time.  For example, the code below
    generates a list of rsync options by replacing time fields with either
    wild cards or specific values according to the requested time range.

       togadirpattern = "%Y-%m-%d-%H*.b"
       dp = datepattern.DatePattern(togadirpattern)
       rsyncopts = dp.generateRsyncRules(times[0], times[1])

    By default time fields are replaced with GlobDatePeriods, but alternate
    periods could be used, such as periods which replace time specifiers
    with regular expression matches.
    """

    def __init__(self, pattern=None, periods=None):
        self.pattern = pattern
        if not periods:
            periods = GlobDatePeriods()
        self.periods = periods
        # If true, the end time is open rather than part of the interval.
        self.exclusive = False

    def setExclusive(self, exclusive):
        self.exclusive = exclusive

    def setPattern(self, pattern):
        self.pattern = pattern

    def formatTime(self, ttime, pattern=None):
        if not pattern:
            pattern = self.pattern
        return _datetime.utcfromtimestamp(ttime).strftime(pattern)

    def generate(self, begin, end, duration=None):
        """
        Generate the date pattern over the given range.

        If a Duration instance is provided, then all time fields of lesser
        duration will be replaced with wildcards.  This reduces the number
        of patterns generated for the given time period, but it may include
        files which do not actually fall within the time period.  For
        example, passing duration=Day will only generate patterns with
        specific day fields, leaving hours, minutes, and seconds as
        wildcards, even though the time period covers only specific hours
        in a day rather than the whole day.  FTP retrievers use this to
        limit the number of directory requests that must be sent,
        preferring instead to filter the final file list on the local side.
        """
        patterns = []
        tt = int(begin)
        # If the interval end time is not inclusive, then exit as soon
        # as the end time reached
        while tt < int(end) or (not self.exclusive and tt <= int(end)):
            # logger.debug("checking time %s" % 
            #              (self.formatTime(tt, "%Y-%m-%d,%H:%M:%S")))
            for p in self.periods.getPeriods():
                if bool(p.containedBy(tt, end) or
                        (duration and p.duration() <= duration.duration())):
                    # All the times in this period are included, so replace
                    # all the lesser periods with wildcards.
                    pattern = self.periods.wildcard(self.pattern, p)
                    pattern = self.formatTime(tt, pattern)
                    # If the pattern still comes out the same as the last
                    # one added (perhaps because the pattern does not even
                    # contain this time field), then ignore it.
                    if not patterns or patterns[-1] != pattern:
                        patterns.append(pattern)
                        logger.debug("found period %s, appending pattern %s" % 
                                     (self.formatTime(tt, "%Y-%m-%d,%H:%M:%S"),
                                      pattern))
                    tt = p.nextPeriod(tt)
                    break
                # If this time does not start on this period, then we have
                # to move to the next smaller period.
            # If all the periods were checked, then at least the seconds
            # should have matched, causing an exact time to be added.
        return patterns

    def generateRsyncRules(self, begin, end):
        patterns = self.generate(begin, end)
        # If the patterns contain directories, then the parent directories
        # of each pattern must be included explicitly also, otherwise the
        # trailing exclude will skip them and the subdirectories will never
        # be traversed.  (See the rsync man page.)  This algorithm adds all
        # the path components up until the last one.
        dirs = []
        for p in patterns:
            comps = p.split("/")
            for i, c in enumerate(comps):
                if i == len(comps)-1:
                    break
                subdir = "/".join(comps[0:i+1])
                if subdir not in dirs:
                    dirs.append(subdir)
	options = []
        options.extend(['--include=%s/' % (d) for d in dirs])
        for p in patterns:
            # We need the extra asterisks if this is a directory, otherwise
            # only the directory gets sync'd and not the contents because
            # of the trailing exclude, and presumably if the pattern is a
            # directory (it ends with a /) then the caller wants to sync
            # the entire contents.
            opt = '--include=%s' % (p)
            # In theory, if the pattern matches filenames, then the **
            # suffix is not needed, and in fact leaving it off avoids
            # accidentally matching directories which match the filename
            # pattern.  However, we have no way of knowing a priori whether
            # the pattern matches filenames or directories, so we require
            # directory patterns to end with a /.
            if opt.endswith('/'):
                opt = opt + "**"
            if opt not in options:
                options.append(opt)
        options.extend(['--exclude=*'])
        return options


def test_period_wildcard():
    dpp = GlobDatePeriods()
    assert dpp.day.wildcard("%Y%m%d") == "%Y%m[0-3][0-9]"
    
def test_glob_wildcard():
    dpp = GlobDatePeriods()
    assert bool(dpp.wildcard("%Y%m%d%H%M%S", dpp.hour) ==
                "%Y%m%d%H[0-5][0-9][0-5][0-9]")

def test_startPeriod():
    dpp = GlobDatePeriods()
    tt = timeFromPtime("20120102030405")
    assert dpp.year.startPeriod(tt) == timeFromPtime("20120101000000")
    assert dpp.month.startPeriod(tt) == timeFromPtime("20120101000000")
    assert dpp.day.startPeriod(tt) == timeFromPtime("20120102000000")
    assert dpp.hour.startPeriod(tt) == timeFromPtime("20120102030000")
    assert dpp.minute.startPeriod(tt) == timeFromPtime("20120102030400")
    assert dpp.second.startPeriod(tt) == timeFromPtime("20120102030405")

    tt = timeFromPtime("20120101000005")
    assert dpp.year.startPeriod(tt) != tt
    assert dpp.month.startPeriod(tt) != tt
    assert dpp.day.startPeriod(tt) != tt
    assert dpp.hour.startPeriod(tt) != tt
    assert dpp.minute.startPeriod(tt) != tt
    assert dpp.second.startPeriod(tt) == tt

    tt = timeFromPtime("20120101000000")
    assert dpp.year.startPeriod(tt) == tt
    assert dpp.month.startPeriod(tt) == tt
    assert dpp.day.startPeriod(tt) == tt
    assert dpp.hour.startPeriod(tt) == tt
    assert dpp.minute.startPeriod(tt) == tt
    assert dpp.second.startPeriod(tt) == tt

    tt = timeFromPtime("20120203000000")
    assert dpp.year.startPeriod(tt) != tt
    assert dpp.month.startPeriod(tt) != tt
    assert dpp.day.startPeriod(tt) == tt
    assert dpp.hour.startPeriod(tt) == tt
    assert dpp.minute.startPeriod(tt) == tt
    assert dpp.second.startPeriod(tt) == tt


def test_nextPeriod():
    dpp = GlobDatePeriods()
    begin = timeFromPtime("20120101000000")
    end = timeFromPtime("20130101000000")
    assert dpp.year.nextPeriod(begin) == end
    begin = timeFromPtime("20000101000000")
    end = timeFromPtime("20010101000000")
    assert dpp.year.nextPeriod(begin) == end


def test_generate_patterns():
    begin = timeFromPtime("200103152208", "%Y%m%d%H%M")
    end = timeFromPtime("200103160123", "%Y%m%d%H%M")
    dp = DatePattern("%Y-%m-%d*")
    assert dp.generate(begin, end) == ["2001-03-15*", "2001-03-16*"]
    dp.setPattern("%Y-%m-%d-%H*")
    assert dp.generate(begin, end) == [ 
        "2001-03-15-22*", "2001-03-15-23*",
        "2001-03-16-00*", "2001-03-16-01*"]


def test_generalize_datepattern():
    # Test the API to limit the number of generated patterns.
    pattern = '%Y%m%d%H%M'
    begin = timeFromPtime("200103152208", "%Y%m%d%H%M")
    end = timeFromPtime("200103160123", "%Y%m%d%H%M")
    dp = DatePattern(pattern)
    plist = dp.generate(begin, end, Day)
    assert plist == ['20010315[0-2][0-9][0-5][0-9]',
                     '20010316[0-2][0-9][0-5][0-9]']

def test_generate_inclusive():
    begin = timeFromPtime("200103152208", "%Y%m%d%H%M")
    end = begin+2
    dp = DatePattern("%H%M%S")
    assert dp.generate(begin, end) == ["220800", "220801", "220802"]

def test_generate_compressed():
    begin = timeFromPtime("200103152258", "%Y%m%d%H%M")
    end = timeFromPtime("200103160103", "%Y%m%d%H%M")
    dp = DatePattern("%H%M%S")
    assert dp.generate(begin, end) == [ 
        "2258[0-5][0-9]",
        "2259[0-5][0-9]",
        "23[0-5][0-9][0-5][0-9]", 
        "00[0-5][0-9][0-5][0-9]",
        "0100[0-5][0-9]",
        "0101[0-5][0-9]",
        "0102[0-5][0-9]",
        "010300"]


def test_generate_rollover():
    begin = timeFromPtime("199912312355", "%Y%m%d%H%M")
    end = timeFromPtime("200001010005", "%Y%m%d%H%M")
    dp = DatePattern("%Y-%m-%d-%H:%M*")
    assert dp.generate(begin, end) == [ 
        "1999-12-31-23:55*",
        "1999-12-31-23:56*",
        "1999-12-31-23:57*",
        "1999-12-31-23:58*",
        "1999-12-31-23:59*",
        "2000-01-01-00:00*",
        "2000-01-01-00:01*",
        "2000-01-01-00:02*",
        "2000-01-01-00:03*",
        "2000-01-01-00:04*",
        "2000-01-01-00:05*"]


def test_generate_mixed():
    begin = timeFromPtime("199912312155", "%Y%m%d%H%M")
    end = timeFromPtime("200001010005", "%Y%m%d%H%M")
    dp = DatePattern("%Y-%m-%d-%H:%M*")
    assert dp.generate(begin, end) == [ 
        "1999-12-31-21:55*",
        "1999-12-31-21:56*",
        "1999-12-31-21:57*",
        "1999-12-31-21:58*",
        "1999-12-31-21:59*",
        "1999-12-31-22:[0-5][0-9]*",
        "1999-12-31-23:[0-5][0-9]*",
        "2000-01-01-00:00*",
        "2000-01-01-00:01*",
        "2000-01-01-00:02*",
        "2000-01-01-00:03*",
        "2000-01-01-00:04*",
        "2000-01-01-00:05*"]


def test_generate_rsync():
    begin = timeFromPtime("201603240000", "%Y%m%d%H%M")
    end = timeFromPtime("201603250000", "%Y%m%d%H%M")
    dp = DatePattern("%y%m%d[NF]F/%H/")
    dp.setExclusive(True)
    opts = dp.generateRsyncRules(begin, end)
    assert opts == ['--include=160324[NF]F/',
                    '--include=160324[NF]F/[0-2][0-9]/',
                    '--include=160324[NF]F/[0-2][0-9]/**',
                    '--exclude=*']

    
    



