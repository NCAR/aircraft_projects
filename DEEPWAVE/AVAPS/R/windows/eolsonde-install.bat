@echo on
@rem This installs all the needed packes once R has been  installed
@rem

@rem Install the needed standard modules from CRAN
Rscript --vanilla -e "install.packages(c('maps','splusTimeDate','splusTimeSeries','quantreg','SparseM','gWidgets2'), repos='http://www.eol.ucar.edu/software/R')"
@rem Install the EOL packages
Rscript --vanilla -e "install.packages(c('eolts','isfs','eolsonde', 'gWidgets2tcltk'), repos='http://www.eol.ucar.edu/software/R')"
@echo Check above for any errors installing the necessary R packages

@pause

@echo Copying Necessary R scripts
copy /Y project_init.R %USERPROFILE%
copy /Y project_plots.R %USERPROFILE%
copy /Y .Rprofile %USERPROFILE%

@rem Navidate to the user profile.  Since we may be installing from a USB (different drive), go to the drive first
%SYSTEMDRIVE%
cd %USERPROFILE%

Rscript --vanilla --restore --save -e "source('project_init.R')"
Rscript --vanilla --restore --save -e "source('project_plots.R')"

@echo Check for errors above 
@pause



