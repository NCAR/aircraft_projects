      SUBROUTINE FLOTE(RMIN,RMAX,MIN,MAJ,DIVS,LINSCL) 
C    &          , Finds a "nice" max and min           MDD <860129.1701>
C 
C *** Written by Mike Daniels, December 1985
C 
      LOGICAL OK,FIRST,DIVS,LINSCL
      DOUBLE PRECISION DIFF,A1,A2,DMIN,DMAX 
      INTEGER*4 MINVAL,MAXVAL 
      PARAMETER (PCT = .65)
      PARAMETER (MAXITR = 100)
      FIRST=.TRUE.
      DIFF=RMAX-RMIN
      OMIN=RMIN 
      OMAX=RMAX 
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
C     WRITE(1,1) RMIN,RMAX
C   1 FORMAT('RMIN,RMAX PASSED TO FLOTE=',2F15.5) 
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
C 
C-----> Take care of the logarithmic scaling case 
C 
      IF (.NOT.LINSCL) THEN 
         DMIN=RMIN
         DMAX=RMAX
         IF (DMIN.GT.0.) A1=DLOG10(DMIN) 
         IF (A1.LT.0..AND.A1.NE.DINT(A1)) THEN
            I1=IDINT(A1-1.) 
          ELSE
            I1=IDINT(A1)
            ENDIF 
         IF (DMAX.GT.0.) A2=DLOG10(DMAX) 
         IF (A2.LT.0..AND.A2.NE.DINT(A2)) THEN
            I2=IDINT(A2-1.) 
          ELSE
            I2=IDINT(A2)
            ENDIF 
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
C        WRITE(1,5) A1,A2,I1,I2 
C  5     FORMAT('A1,A2,I1,I2=',2F15.7,2I5)
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
         RMIN=10.**I1 
         RMAX=10.**I2 
         IF (RMAX.LT.OMAX) THEN 
            I2=I2+1 
            RMAX=10.**I2
            ENDIF 
         IF (I1.EQ.I2) THEN 
            I1=I1-1 
            RMIN=10.**I1
            ENDIF 
         MAJ=ABS(I2-I1) 
         MIN=9
         GOTO 50
         ENDIF
C 
C-----> Get the powers of the difference, maximum, and minimum
C 
      IF (DIFF.EQ.0.) THEN
         RMIN=INT(RMIN)-1.
         RMAX=INT(RMAX)+1.
         MAJ=1
         MIN=2
         GOTO 50
       ELSE 
         PWRD=DLOG10(ABS(DIFF)) 
         ENDIF
      FIRST=.TRUE.
C 
C-----> Subtract one from the difference power to get a close fit 
C 
      IF (PWRD.NE.AINT(PWRD)) PWRD=PWRD-1.
      INPOW=PWRD
C 
C-----> Find a rounded of RMIN and RMAX to the power INPOW
C 
      RMIN=RMIN/(10.**INPOW)
      IF (RMIN.LT.0..AND.RMIN.NE.AINT(RMIN)) RMIN=RMIN-1. 
      RMAX=RMAX/(10.**INPOW)
      IF (RMAX.NE.AINT(RMAX)) RMAX=RMAX+1.
C 
C-----> Store the rounded values as integers so we don't have any round 
C-----> off problems
C 
      MINVAL=RMIN 
      MINVAL=MINVAL*10
      MAXVAL=RMAX 
      MAXVAL=MAXVAL*10
      IF (.NOT.DIVS) GOTO 30
      NTIMES=0
      RMIN=FLOAT(MINVAL)*(10.**(INPOW-1)) 
      RMAX=FLOAT(MAXVAL)*(10.**(INPOW-1)) 
      IF ((DIFF/(RMAX-RMIN)).LT.PCT) GOTO 20
   10 NTIMES=NTIMES+1 
C 
C-----> Check for OK major and minor divisions
C 
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
C     WRITE(1,15) MINVAL,MAXVAL 
C  15 FORMAT(' TRYING DIVISIONS FOR ',2I10) 
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
C 
C-----> See if OK can find good major and minor divisions 
C 
      IF (OK(MINVAL,MAXVAL,MIN,MAJ)) GOTO 30
C 
C-----> Check to see if we have tried too many times
C 
      IF (NTIMES.GT.MAXITR) GOTO 25 
C 
C-----> The first thing we shall try is to raise the maximum or 
C-----> lower the minimum in an alternating sequence
C 
      IF (FIRST) THEN 
         MINVAL=MINVAL-10 
         FIRST=.FALSE.
       ELSE 
         MAXVAL=MAXVAL+10 
         FIRST=.TRUE. 
         END IF 
C 
C-----> If these new maximum and minimum values make the scale too
C-----> large, then lower the power and look at a smaller interval
C 
      RMIN=FLOAT(MINVAL)*(10.**(INPOW-1)) 
      RMAX=FLOAT(MAXVAL)*(10.**(INPOW-1)) 
   20 IF ((DIFF/(RMAX-RMIN)).LT.PCT) THEN 
         INPOW=INPOW-1
         RMIN=OMIN/(10.**INPOW) 
         IF (RMIN.LT.0..AND.RMIN.NE.AINT(RMIN)) RMIN=RMIN-1.
         RMAX=OMAX/(10.**INPOW) 
         IF (RMAX.NE.AINT(RMAX)) RMAX=RMAX+1. 
         MINVAL=RMIN
         MINVAL=MINVAL*10 
         MAXVAL=RMAX
         MAXVAL=MAXVAL*10 
         END IF 
      GOTO 10 
C 
C-----> If we were unsuccessful in finding reasonable values, set 
C-----> the major divisions to 1 and minor divisions so we get at least 
C-----> SOMETHING 
C 
   25 MIN=10
      MAJ=1 
      RMIN=OMIN 
      RMAX=OMAX 
C 
C-----> Restore new values as floating point numbers
C 
   30 RMIN=FLOAT(MINVAL)*(10.**(INPOW-1)) 
      RMAX=FLOAT(MAXVAL)*(10.**(INPOW-1)) 
   50 RETURN
      END 
C 
C 
C 
      LOGICAL FUNCTION OK(MINVAL,MAXVAL,MIN,MAJ)
C    &          , Checks for OK maj and min divisions  MDD <860129.1701>
      INTEGER*4 MINVAL,MAXVAL 
      INTEGER TRY(3),TESTV,DIFFER,DIVS
C 
C-----> MAXMAJ= maximum number of major divisions desired 
C 
      PARAMETER (MAXMAJ = 5)
C 
C-----> MAXMIN= maximum number of minor divisions desired 
C 
      PARAMETER (MAXMIN = 10)
C 
C-----> MINDIV= minimum number of divisions desired 
C 
      PARAMETER (MINDIV = 6)
C 
C-----> MAXDIV= maximum number of divisions desired 
C 
      MAXDIV=MAXMAJ*MAXMIN
      DIFFER=MAXVAL-MINVAL
      TRY(1)=1
      TRY(2)=5
      TRY(3)=2
C 
C-----> Try all tick intervals, 1's, 10's, 5's, 50's, 2's then 20's 
C 
      DO 150 I=1,6
C 
C-----> This obscure equation will give us 1,10,5,50,2,20 in this loop
C 
      TESTV=(TRY((I-1)/2+1)*(10**IABS(MOD(I,2)-1)))*10
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
C     WRITE(1,10) (TESTV/10),DIFFER 
C10   FORMAT('TRYING ',I2,"'S FOR DIFFERENCE OF ",I10)
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
C 
C-----> Go to the next tick interval if this one doesn't divide evenly
C 
      IF (MOD(DIFFER,TESTV).NE.0) GOTO 150
C 
C-----> DIVS contains the total number of divisions 
C 
      DIVS=DIFFER/TESTV 
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
C     WRITE(1,20) DIVS
C20   FORMAT('THIS GIVES ',I4,' DIVISIONS') 
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
C 
C-----> See if DIVS is in the range allowed 
C 
      IF (DIVS.GT.MAXDIV.OR.DIVS.LT.MINDIV) GOTO 150
C 
C-----> Loop through to find number of major and minor divisions
C 
      DO 100 N=MAXMAJ,2,-1
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
C     WRITE(1,30) N,(DIVS/N)
C30   FORMAT('TRYING ',I1,' MAJOR DIVS AND ',I5,' MINOR DIVS')
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
      IF (MOD(DIVS,N).EQ.0.AND.(DIVS/N).LT.MAXMIN) THEN 
         MAJ=N
         MIN=DIVS/N 
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
C        WRITE(1,40)
C40      FORMAT('SUCCESS!') 
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
         GOTO 200 
         END IF 
  100 CONTINUE
  150 CONTINUE
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
C     WRITE(1,150)
C150  FORMAT('NO SUCCESS, RETURNING TO FLOTE')
CDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUGDEBUG 
      OK=.FALSE.
      RETURN
  200 OK=.TRUE. 
      RETURN
      END 
