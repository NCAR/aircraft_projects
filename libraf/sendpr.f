      subroutine sendpr(lu)
      integer*4 system, retval
      character*205 command
      character*7 lpfile
      close(unit=lu)
      if (lu.lt.10) then
         write(lpfile,'("fort.",i1," ")') lu
       else if (lu.lt.100) then
         write(lpfile,'("fort.",i2)') lu
      endif
      command='lpr -s <'//lpfile
      retval=system(command)
      if (retval.ne.0) write(0,10) lpfile,retval
   10 format(' sendpr:Error when sending 'A' to printer, ierr='i5)
      command='rm '//lpfile
      retval=system(command)
      if (retval.ne.0) write(0,20) lpfile,retval
   20 format(' sendpr:Error when removing 'A', ierr='i5)
      return
      end
