/* 
util.c -- utility operations - operations on strings, files, etc.
*/

#include <stdio.h>
#include <constants.h>
#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <sys/param.h>
#include <sys/statvfs.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/utsname.h>
#include <time.h>
#include <utime.h>

#define MAX_FLNM_LNGTH 128

static int StringPosn;

char *strupr();


/*******************************  NINDEX()  *****************************/
int nindex(char *s, char c)
{
int i;
 
 for (i=0; i<strlen(s); i++)
  if ( s[i]==c )
   return i;
 return 0;
} 
 
/***************************************************************************/
char *ResizeMem(void *memptr, int size)
{
 return (char *)realloc((void *)memptr,(size_t)size);
}

/*******************************  SUBSTRING()  *****************************/
char *substring(char *s, char c)
/* return the substring of s that ends just before first occurrence of c
*/
{
 static char *s2=NULL;
 int length;
 
 if (s2)
  (void)free(s2);
 s2=(char *)malloc( (unsigned int)strlen(s));
 length=nindex(s,c);
 if (!length)
  return(NULL);
 (void)strncpy(s2,s,length);
 s2[length]='\0';
 return s2;
}
 
/************************************************************************/
char *ReplaceStringWithChar(string,target,substitute)
char *string,*target,substitute;
{
 int posn,len,posn2,targetlen;

 targetlen=strlen(target);
 for (posn=0; posn<strlen(string); posn++) {
  if (!strncmp(&string[posn],target,targetlen)) {
   string[posn]=substitute;
   for (posn2=posn+1; posn2<posn+targetlen; posn2++)
    string[posn2]=' ';
  }
 }
 return string;
}

/************************************************************************/
int GetNumCharInString(char c, char *s)
{
 int posn,numchars=0;
 for (posn=0; posn<strlen(s); posn++) {
  if (s[posn]==c) 
   numchars++;
 }
 return numchars;
}

/************************* ReplaceChar()  *******************************/
char *ReplaceChar(char *string, char target, char substitute)
{
int posn;

 for (posn=0; posn<strlen(string); posn++) {
  if (string[posn]==target)
   string[posn]=substitute;
 } 
 return string;
}

/***************************************************************************/
char *StripLeadingBlanks(char *s)
{
 int i; 
 int len;

 len=strlen(s);
  
 for (i=0; i<len; i++) 
  if (!isspace(s[i])) { 
   return &s[i]; 
  }
 return NULL;
}

/***********************  TrimTrailingBlanks()  **************************/
char *TrimTrailingBlanks(char *s)
/* remove trailing blanks from character string 
*/ 
{ 
int i; 
int len;

 len=strlen(s);
  
 for (i=len-1; i>=0; i--) 
  if (!(isspace(s[i])) ) { 
/*
with gcc compilation (but not SPARCWorks...), accessing the len'th
position of s results in SEGV. Don't do it. Assume it's already set to
the null character if char just before it is first non-space character found.
*/
   if ((i+1)<len)
    s[i+1]='\0'; 
   return s; 
  }
 return NULL;
} 

/************************  LAST_BLANK()  ***********************************/
int last_blank(char *s, int maxlen)
{
int i;

 if (strlen(s) < maxlen)
  return(strlen(s));

/* find rightmost white space character */
 for (i=MIN(strlen(s),maxlen); i>=0; i--)
  if (isspace(s[i])) {
   return(i);
  }
 return(maxlen);
}

/**********************************  TRIM()  *********************************/
void trim_trailing_blanks(char *s, int len)
/* remove trailing blanks from character string
*/
{
int i;
 
 for (i=len-1; i>0; i--)
  if (!(isspace(s[i])) ) {
   s[i+1]='\0';
   return;
  }
}

/******************  CONCATENATE_()  *********************************/
void concatenate_(char *s1, char *s2)
{
 (void)strcat(s1,s2);
}

/******************  NULL_TERMINATE_()  *********************************/
void null_terminate_(char *s, int *pos)
{
 s[*pos]='\0';
}

/******************  TRIM_TRAILING_DIGITS()  *********************************/
int trim_trailing_digits(char *s, int precision, int retain_decimal)
/* remove trailing zeroes from character string. If character to left of
   rightmost zero is decimal point, restore decimal point and zero IFF 
   retain_decimal is TRUE. Retain at most precision decimal places beyond 
   decimal point. Return length of string.
 
*/
{
int j,i,end;
 
/* find rightmost non-null character */
 for (i=strlen(s)-1; i>=0; i--)
  if (s[i]) {
   end=i;
   break;
  }
 
/* examine leftwards until you reach the decimal point */
 for (i=end; i>=0; i--) {
  if (s[i]!='0') {
   if (s[i]=='.') {   /* s[i] is the decimal point  */
    if (retain_decimal) {
     s[i+1]='0';       /* it was found before any other non-zero digit */
     s[i+2]='\0';
     return(i+2);
    } else {
     s[i]='\0';
     return(i-1);
    }

   } else {   /* s[i] is non-zero -- start by finding the decimal point  */
 for (j=i-1; j>=0; j--) {
     if (s[j]=='.') {    /* s[j] is the decimal point  */
      if (i-j>precision)  /* adjust precision  */
       i=j+precision;
      s[i+1]='\0';
      return(i+1);
     }
    } 
/* whoops  */
    (void)fprintf(stderr,"WARNING: decimal point not found in trim_trailing_digits\n");
    s[i+1]='\0';
    return(i+1);
   }
  } else {  /* s[i] == '0'; remove it for the moment  */
   s[i]='\0';
  }
 } 
/* whoops  */
 (void)fprintf(stderr,"WARNING: non-zero not found in trim_trailing_digits\n");
 return(0);
}

/**************************  SetAlarmTimer() **********************************/

void SetAlarmTimer(int usecs)
/*
set system timer to usecs microseconds, delivering a SIGALRM to process
on timeout
*/
{
static struct itimerval value;
int secs;
/*
disallow usecs values over 1,000,000 (as per man setitimer)
*/
 secs = usecs/1000000;
 usecs = usecs%1000000;
/*
set subsequent timeouts to same as value requested
*/
 value.it_interval.tv_sec=secs;
 value.it_interval.tv_usec=usecs;
 value.it_value.tv_sec=secs;
 value.it_value.tv_usec=usecs;
/*
do it
*/
 setitimer(ITIMER_REAL, &value, (struct itimerval *)NULL);
}

/******************************  SetCurrentDir()  ************************/
int SetCurrentDir(char *dir)
{
 if (!dir)
  return ERROR;
 if (chdir(dir)==ERROR) {
  (void)fprintf(stderr,"problem with chdir to %s: ",dir);
  perror("");
  return ERROR;
 }
 return OK;
}

/******************************  GetCurrentDir()  ************************/
char *GetCurrentDir()
{
static char currentdir[MAXPATHLEN];

 if (!getcwd(currentdir,MAXPATHLEN+1)) {
  (void)fprintf(stderr,"problem with getwd: ");
  perror("");
  return NULL; 
 }
 return currentdir;
}

/**************************  GetUnixCleanFilename() ***********************/
char *GetUnixCleanFilename(char *string)
{
static char CleanFilename[MAX_FLNM_LNGTH];

 (void)sprintf(CleanFilename,"%s",&string[strspn(string," ")]);
 (void)sprintf(CleanFilename,"%s",(char *)ReplaceChar(CleanFilename,'/','-'));
 (void)sprintf(CleanFilename,"%s",(char *)ReplaceChar(CleanFilename,'\'','-'));
 (void)sprintf(CleanFilename,"%s",(char *)ReplaceChar(CleanFilename,'"','-'));
 TrimTrailingBlanks(CleanFilename);
 (void)sprintf(CleanFilename,"%s",(char *)ReplaceChar(CleanFilename,' ','-'));
 return CleanFilename;
}

/******************  TRIM_TRAILING_ZEROS()  *********************************/
void trim_trailing_zeros(char *s)
/* remove trailing zeroes from character string. If character to left of
   rightmost zero is decimal point, restore that zero
*/
{
int i;
 
 for (i=strlen(s)-1; i>0; i--)
  if (s[i]!='0') {
   if (s[i]=='.') {
    s[i+1]='0';
    s[i+2]='\0';
   } else {
    s[i+1]='\0';
   }
   return;
  }
}
/*
internal mgmt on open files
*/
#define MAXOPENFILES 50
struct openfiles {
 int number;
 char *name[MAXOPENFILES];
 int handle[MAXOPENFILES];
};
struct openfiles OpenFiles={0};

/****************************  WINDSShowFiles()  ****************************/
void WINDSShowFiles()
{
  int file;

  /* show open files
   */
  fprintf(stderr,"FILEMGR: there are %d open files\n\n", OpenFiles.number);

  for (file = 0; file < OpenFiles.number; file++)
    fprintf(stderr,"open file: name '%s' fileno %d\n",
		    OpenFiles.name[file], OpenFiles.handle[file]);
}

/************************** WINDSfopen()  **********************************/
FILE *WINDSfopen(char filename[], char mode[])
{
  static FILE *handle;

  if ((handle = fopen(filename,mode)) != NULL) {
    if (OpenFiles.number < MAXOPENFILES-1) {
      OpenFiles.handle[OpenFiles.number] = fileno(handle);
      OpenFiles.name[OpenFiles.number] =
		(char *)malloc((unsigned)(strlen(filename)+1)*sizeof(char));
      strcpy(OpenFiles.name[OpenFiles.number],filename);
      OpenFiles.number++;
    } else {
      WINDSShowFiles();
      fprintf(stderr, "\nFILEMGR WARNING: can't handle anymore open files\n\n");
      }
    }

  return(handle);

}

/************************** WINDSfclose()  **********************************/
void WINDSfclose(FILE *filehandle)
{
int num;

 if (filehandle==NULL)
  return;
 for (num=0; num<OpenFiles.number; num++)
  if (fileno(filehandle)==OpenFiles.handle[num]) {
/*
-1 means this file is now closed
*/
   OpenFiles.handle[num]=-1;
   free(OpenFiles.name[num]);
   OpenFiles.number--;
   (void)fclose(filehandle);
   return;
  }
 (void)fprintf(stderr,"FILEMGR WARNING: filehandle %d not seen in manager\n",
  fileno(filehandle));
 (void)fclose(filehandle);
}

/***************************************************************************/
char *GetNextRecord(int length, FILE *handle, int truncate)
{
 static char InputRecord[1024],*ParsedInput1,*ParsedInput2;

 if (fgets(InputRecord,length,handle)==NULL)
  return NULL;
 if (truncate) {
  ParsedInput1=(char *)substring(InputRecord,'\n');
  if (!ParsedInput1)
   return "";
  ParsedInput2=(char *)TrimTrailingBlanks(ParsedInput1);
  if (!ParsedInput2)
   return ""; 
  return (char *)strdup(ParsedInput2);
 } else {
  return (char *)strdup(InputRecord);
 }
}

/***************************************************************************/

/***
PrintTextFile(filename)
char *filename;
{
 FILE *handle;
 char buffer[1024];

 handle=WINDSfopen(filename,"r");
 while (fgets(buffer,1024,handle)!=NULL) {
  (void)printf("%s",buffer);
 }
 WINDSfclose(handle);
}
***/

#include <signal.h>

static int CoreSignal[]=
{SIGQUIT,SIGILL,SIGTRAP,SIGFPE,SIGBUS,SIGSEGV,SIGSYS,SIGXCPU,SIGXFSZ};
static char CoreSignalName[][16]=
{"SIGQUIT","SIGILL","SIGTRAP","SIGFPE","SIGBUS","SIGSEGV",
"SIGSYS","SIGXCPU","SIGXFSZ"};

static int ExitSignal[]=
{SIGHUP,SIGINT,SIGPIPE,SIGTERM,SIGUSR1,SIGUSR2,SIGPOLL,SIGVTALRM,SIGPROF};
static char ExitSignalName[][16]=
{"SIGHUP","SIGINT","SIGPIPE","SIGTERM","SIGUSR1","SIGUSR2",
"SIGPOLL","SIGVTALRM","SIGPROF"};


/********************** GetCoreSignalName()  *********************************/
char *GetCoreSignalName(int sig)
{
int signal;

 for (signal=0; signal < sizeof(CoreSignal)/sizeof(int); signal++ ) {
  if (sig==CoreSignal[signal])
   return CoreSignalName[signal];
 }
 return "UNKNOWN";
}

/********************** GetExitSignalName()  *********************************/
char *GetExitSignalName(int sig)
{
int signal;

 for (signal=0; signal < sizeof(ExitSignal)/sizeof(int); signal++ ) {
  if (sig==ExitSignal[signal])
   return ExitSignalName[signal];
 }
 return "UNKNOWN";
}

/****************** GetNumberExitSignals()  *********************************/
int GetNumberExitSignals()
{
 return sizeof(ExitSignal)/sizeof(int);
}

/****************** GetNumberCoreSignals()  *********************************/
int GetNumberCoreSignals()
{
 return sizeof(CoreSignal)/sizeof(int);
}

/****************** GetCoreSignal()  *********************************/
int GetCoreSignal(int signal)
{
 return CoreSignal[signal];
}

/****************** GetExitSignal()  *********************************/
int GetExitSignal(int signal)
{
 return ExitSignal[signal];
}

/*****************************  FileExists() ********************************/
bool FileExists(char *filename)
{
  FILE *filehandle;

  if ((filehandle = fopen(filename,"r")) != NULL)
    {
    fclose(filehandle);
    return(TRUE);
    }

  return FALSE;

}

/************************************************************************/
int FileSize(char *filename)
{ 
 struct stat statbuf; 

 if ( (stat(filename,&statbuf)==-1)) {
  perror(filename);
  return -1;
 } else {
  return (statbuf.st_size);
 }
}

/************************************************************************/
bool FileIsSymLink(char *filename)
{
 char buf[64];

 if ( (readlink(filename, (void *)buf, (size_t)64))==-1) {
  return FALSE;
 } else {
  return TRUE;
 }
}

/************************************************************************/
int TimeOfLastUpdate(char *filename) 
{ 
 struct stat statbuf; 

 if ( (stat(filename,&statbuf)==-1)) { 
  perror(filename); 
  return -1; 
 } else { 
  return (statbuf.st_ctime); 
 } 
}

/************************************************************************/
int TimeSinceLastUpdate(char *filename) 
{ 
 struct stat statbuf; 

 if ( (stat(filename,&statbuf)==-1)) { 
  perror(filename); 
  return -1; 
 } else { 
/***
  printf("DEBUG: file: %s; current time: %d; file time: %d; diff: %d\n",
   filename,time((time_t *)NULL),statbuf.st_ctim.tv_sec,
   time((time_t *)NULL)-statbuf.st_ctim.tv_sec);
***/
  return (int)(time((time_t *)NULL)-statbuf.st_ctime); 
 } 
}

/************************************************************************/
int SwapSpaceLeft() 
{ 
 return DiskSpaceLeft("/tmp");
}

/************************************************************************/
int DiskSpaceLeft(char *filesystem) 
{ 
 struct statvfs buf;
 
 if (statvfs(filesystem, &buf)==-1) {   
  perror("statvfs");
  return -1; 
 } else {
  return ((buf.f_frsize*buf.f_bavail)/1000);
 } 
}

/************************************************************************/
void CreateFile(char *filename)
{
  FILE *handle;

  handle=fopen(filename,"w");
  (void)fclose(handle);
}

/************************************************************************/
void TouchFile(char *filename)
{
  utime(filename,NULL);
}

/************************************************************************/
void CreateOrTouchFile(char *filename)
{
  if (FileExists(filename))
    TouchFile(filename);
  else
    CreateFile(filename);
}

static char *FileList;
static int Threshold;

/************************************************************************/
void SetThreshold(int threshold)
{
 Threshold=threshold;
}

/************************************************************************/
int GetThreshold()
{
 return Threshold;
}

/************************************************************************/
void SaveIfLarger(char *filename)
{
int index;

 if (FileSize(filename) > GetThreshold()) {
  index=StringLength(FileList);
  FileList=(char *)realloc((void *)FileList,
   (size_t)(index+strlen(filename)+16));
  (void)sprintf(&FileList[index],"%s %d\n",filename,FileSize(filename)); 
 }
}

/************************************************************************/
char *GetHostName()
{
static struct utsname name;

 if ( (uname(&name)) == -1 ) {
  perror("uname");
  return NULL;
 } else {
  return name.nodename;
 }
}

/************************************************************************/
void LogToStdErr(char msg[])
{
 (void)fprintf(stderr,"%s",msg);
}
 
/************************************************************************/
char * GetTimeStamp()
{
static char timestamp[32];
 
 init_date();
 sprintf(timestamp,"%s %s %s",get_month(),get_day(),GetTime());
 return timestamp;
}

/************************************************************************/
char **GetDirectoryNames(char *parentdir)
{
 DIR *dirp;
 struct dirent *dp;
 static char **Dir=NULL;
 int dir,dirnum=0;
 static int DirSize=0;
 char pathname[512];
 
 dirp=opendir(parentdir);
 if (dirp==NULL) {
  (void)fprintf(stderr,"WARNING: directory open (%s) failed; errno: %d\n",
   parentdir,errno);
  return NULL;
 }
 errno=0;
 while ( (dp = readdir( dirp )) != NULL ) {
  if (strcmp(dp->d_name,".") && strcmp(dp->d_name,"..")) {
   (void)sprintf(pathname,"%s/%s",parentdir,dp->d_name);
   if (IsDirectory(pathname)) {
    int needsize=dirnum+1;
    if (needsize>DirSize) {
     Dir=(char **)ResizeMem(Dir,needsize*sizeof(char *));
     for (dir=DirSize; dir<needsize; dir++) {
      Dir[dir]=NULL; 
     }
     DirSize=needsize;
    } 
    if (Dir[dirnum]) {
     free ((void *)Dir[dirnum]);
     Dir[dirnum]=NULL;
    } 
    Dir[dirnum]=(char *)malloc((unsigned int)strlen(dp->d_name)+1);
    strcpy(Dir[dirnum++],dp->d_name);
   } else {
    continue;
   }
  } 
 } 
 closedir(dirp);
 if (dirnum+1>DirSize) {
  Dir=(char **)ResizeMem(Dir,(dirnum+1)*sizeof(char *));
  DirSize=dirnum+1;
 }
 Dir[dirnum]=NULL;
 return Dir;
}

/************************************************************************/
void FindFiles(char filename[], char directory[], void (*opfunc)(char *), void (*errorfunc)(char *), int lengthcmp)
{
DIR *dirp;
struct dirent *dp;
char pathname[MAX_FLNM_LNGTH];
char errmsg[256];

 dirp=opendir(directory);
 if (dirp==NULL) {
  (void)sprintf(errmsg,"WARNING: directory open (%s) failed; errno: %d\n",
   directory,errno);
  if (errorfunc)
   (*errorfunc)(errmsg);
  else
   (void)fprintf(stderr,"%s",errmsg);
 }
 while ( (dp = readdir( dirp )) != NULL ) {
  if (strcmp(dp->d_name,".") && strcmp(dp->d_name,"..")) {
   (void)sprintf(pathname,"%s/%s",directory,dp->d_name);
   if (IsDirectory(pathname)) {
    FindFiles(filename,pathname,opfunc,errorfunc,lengthcmp);
   } else {
    if (!strlen(filename) || !strcmp(filename,dp->d_name) || 
     (lengthcmp && !strncmp(filename,dp->d_name,lengthcmp))) {
     if (opfunc)
      (*opfunc)(pathname);
     else
      (void)fprintf(stderr,"%s\n",pathname);
    }
   }
  }
 } 
 closedir(dirp);
}

/************************************************************************/
char *ListFilesLargerThan(int threshold, char *directory) 
{
 SetThreshold(threshold);
 if (FileList)
  (void)free(FileList);
 FindFiles("",directory,SaveIfLarger,NULL,FALSE);
 return (char *)FileList;
}

/************************************************************************/
IsDirectory(char pathname[])
{
DIR *dirp;

 if (FileIsSymLink(pathname))
  return FALSE;
 dirp=opendir(pathname);
 if (dirp==NULL)
  return FALSE;
 else {
  closedir(dirp);
  return TRUE;
 }
}

/************************************************************************/
char *GetFileDate(char *filename)
{
static char filedate[32];
char fdate[32];
char ftime[32];
int basetime;

 basetime=TimeOfLastUpdate(filename);
 (void)sprintf(fdate,"%s",(char *)get_date_from_base(basetime));
 (void)sprintf(ftime,"%s",(char *)get_time_from_base(basetime));
 (void)sprintf(filedate,"%s-%s",fdate,ftime);
 return filedate;
}

/************************************************************************/
ExecuteShellCommand(char *command)
{
 FILE *pipe;
 pipe=popen(command,"r");
 pclose(pipe);
}

/************************************************************************/
char *GetShellOutput(char *command, void (*reportfunc)(char *))
{
FILE *pipe;
char string[256];
static char *output;
int index;

 index=0;
 if (!reportfunc && output) {
  (void)free(output);
  output=NULL;
 }
 pipe=popen(command,"r");
 while ( fgets(string,256,pipe) != NULL) {
/*
lose the trailing line feed inherited from fgets()
*/
/*** is this a good idea? 
  (void)sprintf(&string[strlen(string)-1],"\0");
*******/
  if (reportfunc) {
   (*reportfunc)(string);
  } else {
   if (output)
    index=strlen(output);
   output=(char *)realloc ((void *)output,
    ((output?strlen(output):0)+strlen(string)+5)); 
   (void)sprintf(&output[index],"%s",string);
  }
 } 
 pclose(pipe);
 if (!reportfunc)
  return output;
}

/************************************************************************/
 
LogMsgToStdErr(msg)
char *msg;
{
 (void)fprintf(stderr,"%s",msg);
 fflush(stderr);
}
 
/************************************************************************/
 
LogMsgToStdOut(msg)
char *msg;
{
 (void)printf("%s",msg);
 fflush(stdout);
}
 
/************************************************************************/

#include <fmtmsg.h>

LogMsgToConsole(host,source,message)
char *host,*source,*message;
{
 int remote;
 FILE *pipe;
 char rshcmd[1024];
 char *GetComputeHost();

 if (!message)
  return;
 remote=(strlen((char*)GetComputeHost())&&strcmp((char*)GetComputeHost(),host)); if (remote) {
  (void)sprintf(rshcmd,
   "rsh %s \"fmtmsg -u console,print '%s'\"",host,message);
  pipe=popen(rshcmd,"r");
  pclose(pipe);
 } else {
  fmtmsg(MM_PRINT|MM_CONSOLE,(char *)NULL,MM_NOSEV,message,
   (char *)NULL,(char *)NULL); 
 }
}
 
/************************************************************************/

char *
GetFileType(filename)
char *filename;
{
char command[MAX_FLNM_LNGTH+16];
char *filetype;

 (void)sprintf(command,"file %s",filename);
 filetype=(substring((char *)GetShellOutput(command,NULL),'\n'));
 if (filetype)
  return filetype;
 else
  return "Unknown file type";
}

/************************************************************************/

char *
GetCoreType(filename)
char *filename;
{
char command[MAX_FLNM_LNGTH+128];
char *coretype;

 (void)sprintf(command,"file %s | awk '{print $11}'",filename);
 coretype=(substring((char *)GetShellOutput(command,NULL),'\n'));
 if (coretype)
  return coretype;
 else
  return "Unknown-core-type";
}

/************************************************************************/

char *
ShowWINDSStack(filename)
char *filename;
{
char command[MAX_FLNM_LNGTH+128];
char *gdbinfo;

 (void)sprintf(command,"%s/bin/gdb -q -c %s -x %s/scripts/gdb-batch",
  (char *)getenv("GNU"),filename,(char *)getenv("WINDS"));
 gdbinfo=(substring((char *)GetShellOutput(command,NULL),'\n'));
 if (gdbinfo)
  return gdbinfo;
 else
  return "no GDB info";
}

/************************************************************************/

MoveFile(source,dest)
char *source,*dest;
{
char command[MAX_FLNM_LNGTH+128];

 (void)sprintf(command,"/bin/mv %s %s",source,dest);
 ExecuteShellCommand(command);
}

/************************************************************************/
MountingFromNFSServer(server)
char *server;
{
  return(FALSE);
/*
#include <sys/mnttab.h>
struct mnttab mp;
FILE *fp;
int retval,mounting;
char *NFSServer;

 NFSServer=(char *)malloc((unsigned int)strlen(server)+2);
 (void)sprintf(NFSServer,"%s:",server);
 fp=fopen("/etc/mnttab","r");
 mounting=FALSE;
 while ( (retval=getmntent(fp,&mp))!=-1) {
  if ( !(strcmp(mp.mnt_fstype,"nfs"))) {
   if ((char *)strstr(mp.mnt_special,NFSServer)) {
    mounting=TRUE;
    break;
   }
  }
 }
 (void)free(NFSServer);
 (void)fclose(fp);
 return mounting;
*/
}

/************************************************************************/
#include <sys/time.h>
#include <sys/resource.h>
#include <errno.h>

ListLimits()
{
 struct rlimit rlp;

 if (getrlimit(RLIMIT_DATA,&rlp)==-1) {
  (void)fprintf(stderr,"getrlimit RLIMIT_DATA failed, errno %d\n",errno);
 } else {
  (void)fprintf(stderr,"got RLIMIT_DATA\n");
 }
 if (getrlimit(RLIMIT_STACK,&rlp)==-1) {
  (void)fprintf(stderr,"getrlimit RLIMIT_DATA failed, errno %d\n",errno);
 } else { 
  (void)fprintf(stderr,"got RLIMIT_STACK\n");
 }
/*
 if (getrlimit(RLIMIT_VMEM,&rlp)==-1) {
  (void)fprintf(stderr,"getrlimit RLIMIT_DATA failed, errno %d\n",errno);
 } else { 
  (void)fprintf(stderr,"got RLIMIT_VMEM\n");
 }
*/
}

/********************************************************************/
 
LeftJustify(string,target,fieldlen)
char *string,*target;
int fieldlen;
{
 int c;

 (void)sprintf(target,"%s",string);
 for (c=strlen(target); c<fieldlen; c++)
  target[c]=' ';
 (void)sprintf(&target[fieldlen],"\0");
}

/***********************  PadWithBlanks()  **************************/
 
PadWithBlanks(string,length)
char *string;
int length;
{
 int c;
 for (c=0; c<length; c++)
  string[c]=' ';
}

/***********************  GetStringPosition()  **************************/
 
GetStringPosition()
/*
return the most recent value of word position in string sent in call 
to GetNextString()
*/
{
 return StringPosn;
}

/***********************  SetStringPosition()  **************************/
 
SetStringPosition(int posn)
/*
set the value of word position in string sent in call to GetNextString()
*/
{
 StringPosn=posn;
}

/***********************  GetNextString()  **************************/
 
char *
GetNextString(int *posn, char *record)
/*
fetch the next word from the string record as per value of posn, i.e.
if posn==0, get the first word, else get subsequent words. Use a space as
the delimiter between words.
*/
{
static char *string;

 SetStringPosition(*posn);
 string=(char *)strtok((*posn==0?record:(char *)NULL)," ");
 if (string)
  *posn+=strlen(string);
 return string;
}

/***********************  GetNextToken()  **************************/
char *GetNextToken(int *posn, char *record, char *delimiter)
/*
fetch the next word from the string record as per value of posn, i.e.
if posn==0, get the first word, else get subsequent words. Use delimiter as
the delimiter between words.
*/
{
static char *string;

/* SetStringPosition(*posn); */
 string=(char *)strtok((*posn==0?record:(char *)NULL),delimiter);
 if (string)
  *posn+=strlen(string);
 return string;
}

/***********************  StringInList()  **************************/
StringInList(string,list,numlistwords)
char *list[],*string;
int numlistwords;
/*
if string is found in character *list[numlistwords], return
TRUE, else return FALSE
*/
{
int word;

 for (word=0; word<numlistwords; word++) { 
  if (!(strcmp(string,list[word])))
   return TRUE;
 }
 return FALSE;
}

/*************************************************************************/
StringInString(char *s1, char *s2, int caps)
/*
return TRUE if both s1 and s2 are non-NULL and the string s1 is contained in
string s2. If caps is TRUE, consider case-sensitivity, else do not.
*/
{
 char *s1a,*s2a;

 if (!s1 || !s2)
  return FALSE;
 if (strlen(s1)>strlen(s2))
  return FALSE;
 if (!caps) {
  s1a=(char *)strdup(s1); 
  s2a=(char *)strdup(s2);
  return (strstr(strupr(s2a),strupr(s1a))!=NULL);
 } else {
  return (strstr(s2,s1)!=NULL);
 }
}

/*********************************************************************/
int StringCompare(char *s1, char *s2)
{
 if (!s1) {
  if (!s2) {
   return 0;
  } else {
   return 1;
  }
 }
 if (s1[0]!=s2[0])
  return 1;
 return strcmp(s1,s2);
}

/*********************************************************************/

int StringLength(char *string)
{
 if (string)
  return strlen(string);
 else
  return 0;
}

/***********************  TruncateString()  **************************/
char *TruncateString(char *s1, char *s2)
/*
return the string s1 null-terminated at the point where a string matching s2
begins. If s2 does not occur, return s1 as is.

BEWARE: calling side's string (s1) DOES get altered by using this call!
*/
{
char *chopme;

 if ( (chopme=(char *)strstr(s1,s2))!=NULL) {
  s1[strlen(s1)-strlen(chopme)]='\0';
 }
 return s1;
}

