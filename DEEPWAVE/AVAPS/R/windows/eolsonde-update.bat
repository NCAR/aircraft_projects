
rem Update the EOL packages
Rscript --vanilla -e "update.packages(oldPkgs=c('eolts','isfs','eolsonde','gWidgets2tcltk'), repos='http://www.eol.ucar.edu/software/R', ask=FALSE)"

pause
