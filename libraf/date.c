/* 
date.c -- date utility operations
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <utime.h>
#include <sys/time.h>

#include "constants.h"

static int StringPosn;

char *get_month();
char *get_day();
char *get_year();
char *get_date();

/****************************  DATE MODULES  **********************************/

#define NUM_MONTHS 12

static char *date,timestring[9],month[4],day[3],year[3];
static char months[NUM_MONTHS][4]=
{"Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"};
static int date_init=0;

/****************************  INIT_DATE()  **********************************/

init_date()
{ 
long clock;
struct timeval *tp;
struct timezone *tzp;
struct tm *time;

 tp = (struct timeval *)malloc(sizeof(struct timeval));
 tzp = (struct timezone *)malloc(sizeof(struct timezone));
 gettimeofday(tp,tzp);
 clock=(long)tp->tv_sec;
 time=localtime(&clock);
 date=asctime(time);

/* put leading zero on days 1 through 9
*/
 if (date[8]==' ')
  date[8]='0';
 date_init=1;
 (void)free(tp);
 (void)free(tzp);
}

/****************************  GET_MONTH()  **********************************/

char *
get_month()
{
 if (!(date_init))
  init_date();
 (void)strncpy(month,&date[4],3);
 return (month);
}

/*****************************************************************************/

GetMonthNum(month)
char *month;
{
int m;
 
 for (m=0; m<NUM_MONTHS; m++)
  if (!(strcmp(month,months[m])))
   return m;
}

/****************************  GET_MONTH_NUM()  ******************************/

get_month_num()
{
int m;
char *month;
 
 month=get_month();
 for (m=0; m<NUM_MONTHS; m++)
  if (!(strcmp(month,months[m])))
   return m+1;
}

/****************************  GET_DAY()  **********************************/

char *
get_day()
{
 if (!(date_init))
  init_date();
 (void)strncpy(day,&date[8],2);
 return (day);
}

/****************************  GET_YEAR()  **********************************/

char *
get_year()
{
 if (!(date_init))
  init_date();
 (void)strncpy(year,&date[22],2);
 return (year);
}

/****************************  GetTime()  **********************************/

char *
GetTime()
{
 if (!(date_init))
  init_date();
 (void)strncpy(timestring,&date[11],8);
 return (timestring);
}

/****************************  GET_DATE()  **********************************/

char *
get_date()
/* since this returns the current time, always call init_date() first to 
   get current time
*/
{
 init_date();
 return (date);
}

/************************* GetYYMMDDfromBase() ****************************/

char *GetYYMMDDfromBase(basetime)
long basetime;
/*
given a base time, return a string formatted as YYMMDD representing the
year-month-day, with leading zero if needed
*/
{
struct tm *time_info;
static char base_date[9];

 time_info=(struct tm *)gmtime(&basetime);
 (void)sprintf(base_date,"%02d%02d%02d",
  time_info->tm_mon+1,time_info->tm_mday,time_info->tm_year);
 return base_date;
}

/************************  GET_DATE_FROM_BASE()  ******************************/

char *
get_date_from_base(base)
long base;
/*
given a base time since the epoch, initialize a tm struct with
integers representing date and time and return a string with formatted date
*/
{
static char base_date[9];
long basetime;
struct tm *time_info;

 basetime=base;
 time_info=(struct tm *)gmtime(&basetime);
 (void)sprintf(base_date,"%s-%02d-%02d",
  months[time_info->tm_mon],time_info->tm_mday,time_info->tm_year);
 return base_date;
}

/************************  GET_TIME_FROM_BASE()  ******************************/

char *
get_time_from_base(base)
long base;
/*
given a base time since the epoch, initialize a tm struct with
integers representing date and time and return a string with formatted time
*/
{
static char time[9];
long basetime;
struct tm *time_info;

 basetime=base;
 time_info=(struct tm *)gmtime(&basetime);
 (void)sprintf(time,"%02d:%02d:%02d",
  time_info->tm_hour,time_info->tm_min,time_info->tm_sec);
 return time;
}

/*******************************************************************/

GetTimeIntFromHMS(hr,min,sec)
int hr,min,sec;
{
 return hr*10000+min*100+sec;
}

/*******************************************************************/

GetTimeIntFromBase(base)
long base;
{
long basetime;
struct tm *time_info;

 basetime=base;
 time_info=(struct tm *)gmtime(&basetime);
 return time_info->tm_hour*10000+time_info->tm_min*100+time_info->tm_sec;
}

static char TZstring[16];
 
/*******************************************************************/

GetBaseFromMDYHMS(month,day,year,hr,min,sec)
int month,day,year,hr,min,sec;
{
 struct tm time_info;
 int basetime;
 
 time_info.tm_mon=month; 
 time_info.tm_mday=day;
 time_info.tm_year=year;
 time_info.tm_hour=hr;
 time_info.tm_min=min;
 time_info.tm_sec=sec;
 (void)sprintf(TZstring,"%s","TZ=GMT");
 (void)putenv(TZstring);
 basetime=(int)mktime(&time_info);
 return basetime;
}

/************************  HMS2SEC()  ******************************/

int
hms2sec(hr,minut,sec)
int hr,minut,sec;

/* convert integer hour,minutes,seconds to total seconds
*/
{
 if (hr<0 || minut<0 || sec<0)
  return ERROR;
 if (hr>23 || minut>59 || sec>59)
  return ERROR;
 return hr*3600 + minut*60 + sec;
}

int
sec2hms(total,hr,minut,sec)
int total;
int *hr,*minut,*sec;

/* convert integer total seconds to hour, minutes, and seconds
*/
{
 if (total<0) 

/* midnite crossover
*/
  total+=24*3600;
 *hr=total/3600;
 *minut=(int)(((float)total/3600-*hr)*60);
 *sec=total%60;

/* midnite crossover
*/
 *hr=*hr%24;
}

int
next_end_period(total,interval)
int total,interval;

/* given a total seconds (from midnite) and desired interval, return the next
   total seconds that lands "evenly" at the end of a period as prescribed
   by interval.
*/
{
 if (total<0 || interval <=0)
  return ERROR;
 return (total+(interval-(total%interval)));
}

int last_start_period(total,rate,interval)
int total,rate,interval;

/* given a total seconds (from midnite), an update rate, and interval, return 
   previous total seconds that lands "evenly" at the start of a period as 
   prescribed by rate and interval.
*/
{
 if (total<0 || interval <=0 || rate <=0)
  return ERROR;
 if (!(total%interval))
  return total-(rate*interval)+1;
 else {
  int temp;
  temp=total-interval*rate;
  if (temp < 0) 

/* midnite crossover
*/
   temp+=24*3600;
  return next_end_period(temp,interval)+1;
 }
}

/***
main(int argc, char **argv)
{
int basetime;
***/
/*** uncomment this, make date.o, then use gcc date.o -o gethhmmss to create
that binary 
***/
/***
 basetime=atoi(argv[1]);
 printf("%s",get_time_from_base(basetime));
}
***/
/**
 while (1) {
  printf("enter basetime: ");
  scanf("%d",&basetime);
  printf("%s (%s)",
   GetYYMMDDfromBase((long)basetime),get_date_from_base((long)basetime));
 }
***/
/***
uncomment this part, make (date.o), then use

gcc date.o -o getmmyydd

...to create getmmyydd binary

 basetime=atoi(argv[1]);
 printf("%s",GetYYMMDDfromBase((long)basetime));
}
***/
/***
uncomment this part, make (date.o), then use
 
gcc date.c -o getMMM-dd-yy
 
...to create getMMM-dd-yy binary
 
***/
/***
 basetime=atoi(argv[1]);
 printf("%s",get_date_from_base((long)basetime));
}
***/
