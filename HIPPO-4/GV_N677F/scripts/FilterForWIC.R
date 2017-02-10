## ----initialization,echo=FALSE,include=FALSE-----------------------------
args <- commandArgs(trailingOnly = TRUE)

require(knitr)
opts_chunk$set(echo=FALSE, include=FALSE, fig.lp="fig:")
opts_chunk$set(fig.width=6, fig.height=5, fig.pos="center", digits=4)
thisFileName <- "FilterForWIC"
require(Ranadu, quietly = TRUE, warn.conflicts=FALSE)
require(ggplot2)
require(grid)
require(ggthemes)
require(ncdf4)
run.args <- commandArgs (TRUE)
Directory <- "/scr/raf/Prod_Data/"
Flight <- "rf02" 		  # XXX change this or use command arguments
Project = "HIPPO-5"		 # XXX change this or use command arguments
ProjectDir <- "HIPPO"
Wchoice <- "WIF"                #default choice for WIX is WIF
if (length (run.args) > 0) {Project <- run.args[1]}
if (length (run.args) > 1) {Flight <- run.args[2]}
if (length (run.args) > 2) {ProjectDir <- run.args[3]}
if (length (run.args) > 3) {Wchoice <- run.args[4]}
if (!Wchoice %in% c("WIF", "WIC")) {
  print (sprintf ("invalid argument %s for Wchoice; exiting", Wchoice))
  quit(save="no")
}
CutoffFreq <- 600
if (length (run.args) > 3) {CutoffFreq <- numeric(run.args[4])}
fname = sprintf("%s/%s/%s%s.nc", Directory,ProjectDir,Project,Flight)
fnew  = sprintf("%s/%s/%s%sF.nc", Directory,ProjectDir,Project,Flight)

## beware: overwrites without warning!!
Z <- file.copy (fname, fnew, overwrite=TRUE)  ## BEWARE: overwrites without warning!!

SaveRData <- sprintf("%s.Rdata", thisFileName)
ReloadData <- TRUE    ## can only use FALSE with repeat of same flight
if (ReloadData) {
  Data <- getNetCDF (fname, c("WIC"))		#XXX set variables needed here
  save(Data, file=SaveRData)
} else {
  load (SaveRData)
}


## ----get-netCDF-file, include=TRUE---------------------------------------

netCDFfile <- nc_open (fnew, write=TRUE) 
Rate <- 1
Dimensions <- attr (Data, "Dimensions")
Dim <- Dimensions[["Time"]]
if ("sps25" %in% names (Dimensions)) {
  Rate <- 25
  Dim <- list(Dimensions[["sps25"]], Dimensions[["Time"]])
}
if ("sps50" %in% names (Dimensions)) {
  Rate <- 50
  Dim <- list(Dimensions[["sps50"]], Dimensions[["Time"]])
}


## ----filter-WIC, include=TRUE, fig.cap="Comparison of unfiltered and filtered values for the vertical wind.", echo=TRUE----

CutoffFreq <- 600 * Rate    ## Rate is defined above, 
                            ## 1 or 25 for std or high-rate file
d <- zoo::na.approx (as.vector(Data$WIC), maxgap=100*Rate, na.rm = FALSE)
d[is.na(d)] <- 0
Data$WIF <- Data$WIC - signal::filtfilt( signal::butter (3, 1/CutoffFreq), d)
plotWAC(Data[, c("Time", "WIC", "WIF")]) 
title(sprintf("Project %s Flight %s", Project, Flight))


## ----add-to-netCDF-file--------------------------------------------------

# copy attributes from old variable (e.g., WIC) to new one (e.g., WIF)
copy_attributes <- function (atv, v, nfile) {
  for (i in 1:length(atv)) {
    aname <- names(atv[i])
    if (grepl ('name', aname)) {next}  # skips long and standard names
    if (grepl ('units', aname)) {next}
    if (grepl ('Dependencies', aname)) {next}
    if (grepl ('actual_range', aname)) {next}
    if (is.numeric (atv[[i]])) {
      ncatt_put (nfile, v, attname=aname, attval=as.numeric(atv[[i]]))
    } else {
      ncatt_put (nfile, v, attname=aname, attval=as.character (atv[[i]]))
    }
  }
}

varF <- ncvar_def ("WIF", 
                    units="m/s", 
                    dim=Dim, 
                    missval=as.single(-32767.), prec='float', 
                    longname="WIC, high-pass-filtered")
varX <- ncvar_def ("WIX", 
                    units="m/s", 
                    dim=Dim, 
                    missval=as.single(-32767.), prec='float', 
                    longname="preferred variable for vertical wind")
newfile <- ncvar_add (netCDFfile, varF)
newfile <- ncvar_add (newfile, varX)

ATV <- ncatt_get (netCDFfile, "WIC")
V <- "WIF"
copy_attributes (ATV, V, newfile)
ncatt_put (newfile, V, attname="standard_name", 
           attval="filtered_vertical_wind")
ncatt_put (newfile, V, attname="Dependencies", 
           attval="1 WIC")
ncatt_put (newfile, V, attname="filter_time_constant",
           attval=sprintf("%d s", CutoffFreq))

V <- "WIX"
copy_attributes (ATV, V, newfile)
ncatt_put (newfile, V, attname="standard_name", 
           attval="best_vertical_wind")
ncatt_put (newfile, V, attname="Dependencies", 
           attval=sprintf ("1 %s", Wchoice))
if (Rate == 1) {
  ncvar_put (newfile, varF, Data$WIF)
  ncvar_put (newfile, varX, Data[, Wchoice])
} else if (Rate == 25) {
  ncvar_put (newfile, varF, Data$WIF, count=c(25, nrow(Data)/25))
  ncvar_put (newfile, varX, Data[, Wchoice], count=c(25, nrow(Data)/25))
} else if (DataRate == 50) {
  ncvar_put (newfile, varF, Data$WIF, count=c(50, nrow(Data)/50))
  ncvar_put (newfile, varX, Data[, Wchoice], count=c(50, nrow(Data)/50))
}
nc_close (newfile)


## ----save-system-info, echo=FALSE----------------------------------------
cat (toLatex(sessionInfo()), file="SessionInfo")


## ----make-zip-archive, echo=TRUE, INCLUDE=TRUE, eval=TRUE----------------
system (sprintf("zip %s.zip %s.Rnw %s.pdf Workflow%s.pdf DGF.dot SessionInfo %s", thisFileName, thisFileName, thisFileName, thisFileName, SaveRData))


## ----make-workflow-diagram, echo=FALSE, eval=FALSE-----------------------
## 
## library(DiagrammeR)
## grViz ("DGF.dot", engine='dot')
## 

