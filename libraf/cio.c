/*  FILE: cio.c  */
/*  C functions to write bytes to UNIX files - called from FORTRAN */
/*  copen
    bnread
    bnwrit
    cclose  
    rewtap
    eoftap
    fsftap 
    bsftap
    bsrtap
    bsrfil */
/*  870417  */

#include <stdio.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/mtio.h>
#include <sys/ioctl.h>
#include <sys/uio.h> 
#include <tapeerr.h>

/* ****************************************************************** */
 
 copen_ (unit, nunit, name, mode, err, oflag)
   int *unit, *nunit, *mode, *err, *oflag;
   char name[40]; 
 
 /* unit = Fortran unit number
    nunit = UNIX file descriptor associated with 'unit'
    name  = UNIX file name
    mode = 0 : write only - file will be created if it doesn't exist
                          - otherwise will be rewritten
         = 1 : read  only
         = 2 : read/write 
    oflag = 0 : no notification if file opened OK
          = 1 : file name and unit number printed */
  {
   int i,fd,err2,drive,dens;
   char fname[40],cmd[40];
   extern int errno;        /* I/O error return */

   if (*oflag != 0)
     printf ("Copen: File = %s Fortran Unit = %d   ", name, *unit);

   /* strip trailing blanks and add null character to name */
   for (i=0; name[i]!=' ' && name[i]!='\0' && i<40; ++i)
     fname[i] = name[i];
   fname[i] = '\0';

/* if (*mode == 0)    WRITE ONLY 
   printf ("UNIX File descriptor: %d\n", fd = open (fname, O_WRONLY));
     printf ("UNIX File descriptor: %d\n", fd = creat (fname, 0777));
   else if (*mode == 1)   READ ONLY 
     printf ("UNIX File descriptor: %d\n", fd = open (fname, O_RDONLY));
   else   READ/WRITE 
     printf ("UNIX File descriptor: %d\n", fd = open (fname, O_RDWR));*/
/*
   brkuptp(fname,&drive,&dens);
   sprintf(cmd,"assign -m%1d %4d",drive,dens);
   err2=system(cmd);
*/
   if (*mode == 0)              /* WRITE ONLY */
      fd = creat (fname, 0777);
   else if (*mode == 1)         /* READ ONLY */
      fd = open (fname, O_RDONLY);
   else                         /* READ/WRITE */
      fd = open (fname, O_RDWR);
   if (*oflag != 0)
      printf ("UNIX File descriptor: %d\n", fd);
 
   *err = 0;
   if (fd == -1)           /* error opening file */
     {
      printf ("Error opening %s  Error status: %d\n", fname, errno);
      perror ("copen.c");
      *err = errno;
     }

   *nunit = fd;
   return;
  }

/* ****************************************************************** */

 bnread_ (fd, buf, nbuf, bread, ios, idiag)
   int *fd, *nbuf, buf[], *bread, *ios, *idiag; 
  /* fd = UNIX file descriptor number (NOT a Fortran unit)
     buf = area into which to read
     nbuf = number of bytes to read from fd
     bread = number actually read 
     ios = error number returned to Fortran 
     idiag : if non-zero, error and EOF messages will be printed */

  {
   int bytesread,idum;
   struct mtget tape_stat;

   /* printf ("BNREAD Fd = %d Nbuf = %d\n", *fd, *nbuf); */
   bytesread = read (*fd, buf, *nbuf);  
   idum=ioctl(*fd,MTIOCGET,&tape_stat);
   
   /* printf ("Bytes %d   stat %d\n", bytesread, errno);  */

   if (bytesread == -1)           /* error reading file */
     {
      if (*idiag != 0)
        printf ("Error reading C unit %d Error status=%d\n", *fd,tape_stat.mt_dsreg);
      perror ("bnread.c");
      *ios = tape_stat.mt_dsreg;
     }
   else if (bytesread == 0)       /* end-of-file on input */
     {
      if (*idiag != 0)
        printf ("End of file on C unit %d\n", *fd);
      *ios = tape_stat.mt_dsreg;
     }
   else                           /* read OK */
     {
      /* printf ("BNREAD - bytes read = %d   Buf = %d %d %d\n",
        bytesread, buf[0], buf[1], buf[2]); */
      *ios = 0;
     }

   *bread = bytesread;
   return;
  }
/* ****************************************************************** */

 bnwrit_ (fd, buf, nbuf, bwritten, err, idiag)
   int *fd, *nbuf, buf[], *bwritten, *err, *idiag; 
  /* fd = UNIX file descriptor number (NOT a Fortran unit)
     buf = area from which to write
     nbuf = number of bytes to write to fd
     bwritten = number actually written 
     err = UNIX error number returned to FORTRAN 
     idiag : if non-zero, error and EOF messages will be printed */

  {
   int byteswritten;
   int idum;
   struct mtget tape_stat;

 /* printf ("BNWRIT Fd = %d Nbuf = %d   Buf = %d %d %d\n",
      *fd, *nbuf, buf[0], buf[1], buf[2]);*/ 
   byteswritten = write (*fd, buf, *nbuf);  
   idum=ioctl(*fd,MTIOCGET,&tape_stat);
 /*   printf ("Bytes %d   stat %d\n", byteswritten, errno);*/  

   *err = 0;
   if (byteswritten == -1)           /* error writing file */
     {
      if (*idiag != 0)
        printf ("Error writing C unit %d\n", *fd);
      perror ("bnwrit.c");
      *err = tape_stat.mt_dsreg;
     }

   *bwritten = byteswritten;
   return;
  }

/* ****************************************************************** */
 
 cclose_ (nunit, stat, err)
   int *nunit, *stat, *err;
  {
   extern int errno;        /* I/O error return */
   struct mtop tapeop;
   int i,istat;

   /* printf ("Cclose: Nunit = %d Error status: %d Error #: %d\n",
      *nunit, istat = close (*nunit), errno); */
   tapeop.mt_op=MTOFFL;
   tapeop.mt_count=1;
   i=ioctl(*nunit,MTIOCTOP,&tapeop);
   istat = close (*nunit);
   if (istat == 0)
     printf ("Cclose successful: Nunit = %d \n", *nunit);

   *stat = istat;
   *err  = 0;
   if (istat == -1)           /* error closing file */
     {
      printf ("Error closing %d\n", *nunit);
      perror ("cclose.c");
      *err  = errno;
     }
/*
   i=system("deassign");
*/
   return;
  }

/* ****************************************************************** */
 
 rewtap_ (fd, stat, err)
   int *fd, *stat, *err;
  {
   extern int errno;        /* I/O error return */
   extern char *sys_errlist[];  /* system I/O error messages */
   int istat;
   struct mtop mtsetup;     /* mag tape setup structure */

   mtsetup.mt_count = 1;
   mtsetup.mt_op    = MTREW;
   if (ioctl (*fd, MTIOCTOP, &mtsetup))
     { 
       printf (" Tape error on rewind: %d, %s\n",
                 errno, sys_errlist[errno]);
       exit (1);
     }
   else
     printf (" Fd %d rewound.\n", *fd);

   return;
  }
 
/* ****************************************************************** */
 
 eoftap_ (fd, stat, err)
   int *fd, *stat, *err;
  {
   extern int errno;        /* I/O error return */
   extern char *sys_errlist[];  /* system I/O error messages */
   int istat;
   struct mtop mtsetup;     /* mag tape setup structure */

   mtsetup.mt_count = 1;
   mtsetup.mt_op    = MTWEOF;
   if (ioctl (*fd, MTIOCTOP, &mtsetup))
     { 
       printf (" Tape error on writing EOF to fd %d: %d, %s\n",
                 *fd, errno, sys_errlist[errno]);
       exit (1);
     }

   return;
   }
 
/* ****************************************************************** */
 
 fsftap_ (fd, stat, err)
   int *fd, *stat, *err;  /* FORWARD SPACE FILE ON TAPE UNIT */
  {
   extern int errno;        /* I/O error return */
   extern char *sys_errlist[];  /* system I/O error messages */
   int istat;
   struct mtop mtsetup;     /* mag tape setup structure */

   mtsetup.mt_count = 1;
   mtsetup.mt_op    = MTFSF;
   if (ioctl (*fd, MTIOCTOP, &mtsetup))
     { 
       printf (" Tape error on FSF: %d, %s\n",
                 errno, sys_errlist[errno]);
       exit (1);
     }

   return;
   }

/* ****************************************************************** */
 
 bsftap_ (fd, stat, err)
   int *fd, *stat, *err;  /* BACKWARD SPACE FILE ON TAPE UNIT */
  {
   extern int errno;        /* I/O error return */
   extern char *sys_errlist[];  /* system I/O error messages */
   int istat;
   struct mtop mtsetup;     /* mag tape setup structure */

   mtsetup.mt_count = 1;
   mtsetup.mt_op    = MTBSF;
   if (ioctl (*fd, MTIOCTOP, &mtsetup))
     { 
       printf (" Tape error on BSF: %d, %s\n",
                 errno, sys_errlist[errno]);
       exit (1);
     }

   return;
   }

/* ****************************************************************** */
 
 bsrtap_ (fd, stat, err)
  int *fd, *stat, *err;  /* BACK SPACE RECORD ON TAPE UNIT */
  {
   extern int errno;        /* I/O error return */
   extern char *sys_errlist[];  /* system I/O error messages */
   int istat;
   struct mtop mtsetup;     /* mag tape setup structure */

   mtsetup.mt_count = 1;
   mtsetup.mt_op    = MTBSR;
   if (ioctl (*fd, MTIOCTOP, &mtsetup))
     { 
       printf (" Tape error on BSR: %d, %s\n",
                 errno, sys_errlist[errno]);
       exit (1);
     }

   return;
   }

/* ****************************************************************** */
 
 bsrfil_ (fd, reclen, stat, err)
  int *fd, *reclen, *stat, *err;  /* BACK SPACE RECORD ON FILE */
  {
   extern int errno;        /* I/O error return */
   extern char *sys_errlist[];  /* system I/O error messages */
   int mode, irec, fp;

   mode = 1; /* relative positioning */
   irec = -*reclen;
   printf (" bsrfil: file descriptor  = %d\n", *fd);
   printf (" bsrfil: irec = %d   mode = %d\n", irec, mode);
   printf ("File position = %d\n", fp = (lseek (*fd, irec, 1L)));
   if (fp < 0)
     { 
       printf (" File error on BSR: %d, %s\n",
                 errno, sys_errlist[errno]);
       exit (1);
     }

   return;
   }
int brkuptp(devname,num,dens)
  char *devname;
  int *num,*dens;
{
  int i,j;
  while (*devname)
     devname++;
  devname--;
  sscanf(devname,"%1d",num);
  devname-=6;
  sscanf(devname,"%4d",dens);
}
