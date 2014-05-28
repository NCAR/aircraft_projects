
\R\bin\Rscript --vanilla -e "remove.packages(c('eolts','isfs','eolsonde'))"


\R\bin\Rscript --vanilla -e "install.packages(c('f:/eolts_0.0-290.zip','f:/isfs_0.0-290.zip','f:/eolsonde_2.4-290.zip'),repos=NULL,type='win.binary')"
