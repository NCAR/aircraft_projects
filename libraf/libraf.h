extern "C" {
void *ResizeMem(void *object,int size);
int StringInString(char *s1,char *s2,int caps);
char * TruncateString(char *s1,char *s2);
int StringCompare(char *s1,char *s2);
char * GetNextString( int *posn,char *record);
char * GetCurrentDir();
int SetCurrentDir(char *);
char * GetShellOutput(char *,void (*)(char *));
char * StripLeadingBlanks(char *);
char *GetNextRecord(int,FILE *,int);
char *GetNextToken(int*,char*,char *);
char **GetDirectoryNames(char *);
char *IsDirectory(char *);
char *ReplaceStringWithChar(char *,char *,char);
char *get_date_from_base(long);
char *get_time_from_base(long);
}
