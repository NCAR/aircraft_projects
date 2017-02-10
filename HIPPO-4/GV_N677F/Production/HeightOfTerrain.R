## ----initialization,echo=FALSE,include=FALSE-----------------------------

writeLines("This script must be run from barolo as libraries aren't currently installed elsewhere")

args <- commandArgs(trailingOnly = TRUE)
TdbData <- "/h/eol/janine/Rstudio/HeightOfTerrain/TerrainData"

if (length(args) == 8) {
   print("Using values from command line")
   Project = args[1] ## project name in caps
   Flight <- args[2] ##rfxx
   Directory <- args[3]
   lt_s <- args[4]
   lt_n <- args[5]
   lg_w <- args[6]
   lg_e <- args[7]
   Tdb <- args[8]
} else if (length(args) == 0) {
   print("Using hardcoded values. Don't forget to change lat/lon!")
   Flight <- "rf01" 		
   Project = "DEEPWAVE"	
   Directory <- "/scr/raf/Prod_Data/$Project"
   #range for DEEPWAVE
   lt_s <- -60
   lt_n <- -20 
   lg_w <- 130 
   lg_e <- -150 
   # range for NOMADSS&FRAPPE: had to download G13 to L19
   #lt_s <- 24 # N
   #lt_n <- 45 # N
   #lg_w <- -111 # W -- used 106 to get exactly 105 to work
   #lg_e <-  -72 # W
   Tdb <- "yes"
} else {
   writeLines("Usage: \n\tTo use in RStudio browser window, edit hard-coded flight and project name above and run. \n\t To use at the command line, give project name in caps and flight number with lower case [rtf] as command line arguments, e.g. \n\t\tRscript HeightOfTerrain.R $project $flight lt_s lt_n lg_w lg_e Tdb")
   quit()
}

library(knitr)
library(RCurl)
opts_chunk$set(echo=FALSE, include=FALSE, fig.lp="fig:", size='small')
opts_chunk$set(fig.width=6, fig.height=5, fig.pos="center", digits=4)
thisFileName <- "HeightOfTerrain"
require(Ranadu, quietly = TRUE, warn.conflicts=FALSE)
require(ggplot2)
require(grid)
require(ggthemes)
require(sm)
require(plyr)
require(ncdf4)
require(maps)
fname = sprintf("%s/%s%s.nc", Directory,Project, Flight)
SaveRData <- sprintf("%s.Rdata.gz", thisFileName)
print(sprintf("Processing %s %s",fname,Tdb))

## ----download-zip-files, echo=TRUE, include=TRUE, cache=TRUE-------------
if (identical(Tdb,"yes")) {
   # there must be a subdirectory named 'TerrainData' 
   setwd (TdbData)    # Save the data in a subdirectory 
   ###### next are the limits for the range to download
   ## each zip file contains 4 deg latitude x 6 deg longitude, for the source used
   #     (http://www.viewfinderpanoramas.org/dem3.html)
   #     Acknowledgement: Jonathan de Ferranti BA
   #                      Lochmill Farm
   #                      Newburgh, Fife, KY14 6EX, United Kingdom
   ## Identifier for individual files is lat/lon at SE corner
   #  Identifier for zip files containing 4 x 6 individual files is 
   # [none/S]LetterNmbr where
   ## for US, e.g., NOMADSS, indices are as follows:
   #      letter = LETTER[floor (lat/4) + 1]
   #      Nmbr = 30 + floor (lon/6) + 1
   ###### loop through the needed files
   for (lt in lt_s:lt_n) {    # latitude limits (note 'N' or 'S' in sprintf statement) 
     ifelse (lt >= 0, NS <- 'N', NS <- 'S')
     # Deal with crossing 180 -> -180
     if (lg_w > lg_e) {
       lrange = c(lg_w:180,-180:lg_e)
     } else {
       lrange = lg_w:lg_e
     }
     for (lg in lrange) {   # longitude limits (note 'E' or 'W') 
       ifelse (lg >= 0, EW <- 'E', EW <- 'W')
       sname <- sprintf("Z%s%d%s%03d.gz", NS, abs(lt), EW, abs(lg)) 
       dname <- sprintf ("%s%02d%s%03d.hgt", NS, abs(lt), EW, abs(lg)) # a sq. degree of data 
       if (file.exists(sname)) {   # Skip if file is already present 
         unlink (dname)  
       } else {
   # is it already there from a previous download?
         if (file.exists (dname)) {
           #                # 'swap' changes from big-endian to little-endian 
           height <- readBin (dname, 'int', size=2, n=1201*1201, endian='swap')
           height [height == -32768] <- NA     # set NA for missing values 
           dim (height) <- c(1201,1201)        # Make into a matrix 
           save (height, file=sname, compress='gzip') 
           unlink (dname) # delete the unzipped file 
         } else {
   # find the database file that contains this:
           lettr <- floor (lt %/% 4) + 1
           numbr  <- 30 + floor (lg %/% 6) + 1
           if (lt < 0) {
             zipFileName <- sprintf ("S%s%02d.zip", LETTERS[1-lettr], numbr)
           } else {
             zipFileName <- sprintf ("%s%02d.zip", LETTERS[lettr], numbr)
           }
         # sprintf(" needed zip file is %s", zipFileName)
         # if it's already present, skip download
           if (!file.exists(zipFileName)) {
             url <- sprintf("http://www.viewfinderpanoramas.org/dem3/%s", zipFileName)
             if (RCurl::url.exists (url, followlocation=FALSE)) { # there are false moved-URLs ...
               f = RCurl::CFILE(zipFileName, mode="wb")
               RCurl::curlPerform(url = url, writedata = f@ref)
               on.exit(close(f))
               unzip (zipFileName, junkpaths=TRUE)
               unlink (zipFileName)
               system (sprintf("touch %s", zipFileName))
               ## The reason for the preceding statement is to prevent trying to
               ## download repeatedly in cases where the file is not present, for
               ## example because it is entirely over ocean.
             }
           }
         }
         if (file.exists(dname)) {
           height <- readBin (dname, 'int', size=2, n=1201*1201, endian='swap')
           height [height == -32768] <- NA     # set missing values to NA
           dim (height) <- c(1201,1201)        # Make into a matrix 
           save (height, file=sname, compress='gzip') 
           unlink (dname) # delete the unzipped file 
         } 
       } 
     } 
   }
   setwd(".")
   print("Done loading Terrain Database")
} else {
   print("Skip loading Terrain Database")
}

## ----height-function, echo=TRUE, include=TRUE----------------------------

HeightOfTerrain <- function (.lat, .long) { 
  lt <- as.integer (floor(.lat)) 
  lg <- as.integer (floor(.long)) 
  if (is.na(lt) || is.na(lg)) {return (NA)} # beware of bad input
  if (lt < 0) { 
    NS <- "S" 
    lt <- -lt 
  } else {
    NS <- "N" 
  } 
  if (lg < 0) {
    EW <- "W" 
    lg <- -lg 
  } else { 
    EW <- "E" 
  } 
  vname <- sprintf("Z%s%02d%s%03d", NS, lt, EW, lg) 
  if (!exists(vname, .GlobalEnv)) { 
    zfile <- sprintf("%s.gz", vname)
    print (zfile)
    if (file.exists(sprintf("%s/%s",TdbData,zfile))) {
      load(file=sprintf("%s/%s.gz", TdbData,vname)) 
      assign (vname, height, envir=.GlobalEnv)
    } else { 
      return (NA) 
    } 
  } 
  ix <- as.integer ((.long - floor (.long) + 1/2400) * 1200) + 1 
  iy <- as.integer ((ceiling (.lat) - .lat + 1/2400) * 1200) + 1
  if (ceiling (.lat) == .lat) { # exact match fails; correct it
    iy <- 1201
  }
  hgt <- get(vname, envir=.GlobalEnv)[ix, iy] 
  return (hgt) 
}

## ----USGS-test, echo=TRUE, include=TRUE, warning=FALSE,message=FALSE, eval=FALSE----
## 
## require(RCurl)
## n <- 5000
## HOT <- vector ("numeric", n)
## USGS <- vector ("numeric", n)
## ltt <- runif (n, lt_s, lt_n)
## lgg <- runif (n, lg_w, lg_e)
## for (i in 1:n) {
##   HOT[i] <- HeightOfTerrain (ltt[i], lgg[i])
##   url <- sprintf ("http://137.227.248.58/pqs.php?x=%f&y=%f&units=Meters&output=json", lgg[i], ltt[i])
##   USGS[i] <- as.numeric (strsplit (strsplit (RCurl::getURL(url), 'Elevation\":')[[1]][2], ',.*'))
## }
## meanDiff <- mean (HOT-USGS, na.rm=TRUE)
## sdDiff <- sd (HOT-USGS, na.rm=TRUE)
## print (sprintf ("mean difference: %f", meanDiff))
## print (sprintf ("std dev: %f", sdDiff))
## hist (HOT-USGS, breaks=50, xlim=c(-10,10))

## ----add-variables-to-netCDF-file, echo=TRUE, include=TRUE---------------

fname <- sprintf("%s/%s%s.nc", Directory, Project, Flight)
fnew <- sprintf("%s/%s%sZ.nc", Directory, Project, Flight) 
print(sprintf("Copy file %s to %s",fname,fnew))
# copy file to avoid changing original: note 'Z' in new file name
file.copy (fname, fnew, overwrite=TRUE)   #careful: will overwrite 'Z' file
# load data needed to calculate the new variables:
#   ... there is no GGALTB in NOMADSS files? (What is GGALTC?) Use GGALT
Data <- getNetCDF (fnew, c("LATC", "LONC", "GGALT")) 
SFC <- vector ("numeric", length (Data$Time)) 
netCDFfile <- nc_open(fnew, write=TRUE) 
# have to use a loop here because HeightOfTerrain looks
# up and loads needed files so is not suited to vector ops
for (i in 1:length (Data$Time)) {
  if (is.na (Data$LONC[i]) || is.na (Data$LATC[i])) {
    SFC[i] <- NA
  } else {
    SFC[i] <- HeightOfTerrain (Data$LATC[i], Data$LONC[i]) 
  }
} 

# replace missing values with interpolated values for gaps up to 10 s in length:
# Check if have at least two non-NA values in SFC. If not, fill all NA's
# with zeros.
if (!all(is.na(SFC))) {
    SFC <- zoo::na.approx (SFC, maxgap=10, na.rm = FALSE) 
} 
SFC[is.na(SFC)] <- 0      # replace missing values with zero; mostly ocean pts
ALTG <- Data$GGALT - SFC 
Data["SFC_SRTM"] <- SFC   # add new variable to data.frame
Data["ALTG_SRTM"] <- ALTG
SaveRData <- "NOMADSSterrain.Rdata.gz"
# comment one of these
save(Data, file=SaveRData, compress="gzip")
# load(file=SaveRData)


## ----modify-netCDF-file, tidy=TRUE, tidy.opts=list(width=60)-------------

varSFC <- ncvar_def ("SFC_SRTM", "m", netCDFfile$dim["Time"], -32767., 
                        "Elevation of the Earth's surface below the aircraft position, WGS-84") 
varALTG <- ncvar_def ("ALTG_SRTM", "m", netCDFfile$dim["Time"], -32767., 
                         "Altitude of the aircraft above the Earth's surface, WGS-84")
newfile <- ncvar_add (netCDFfile, varSFC)
ncatt_put (newfile, "SFC_SRTM", attname='DataSource', 
              attval="viewfinderpanorama Jonathan de Ferranti")
ncatt_put (newfile, "SFC_SRTM", attname="Category", attval="Position")
ncatt_put (newfile, "SFC_SRTM", attname="Dependencies", attval="2 LATC LONC")
minmax <- sprintf ("%.0f.f,%.0f.f", min (SFC, na.rm=TRUE), max (SFC, na.rm=TRUE))
ncatt_put (newfile, "SFC_SRTM", attname="actual_range", attval=minmax)
newfile <- ncvar_add (newfile, varALTG)
ncatt_put (newfile, "ALTG_SRTM", attname="DataSource", attval="viewfinderpanorama Jonathan de Ferranti")
ncatt_put (newfile, "ALTG_SRTM", attname="Category", attval="Position")
ncatt_put (newfile, "ALTG_SRTM", attname="Dependencies", attval="2 SFC_SRTM GGALT")
minmax2 <- sprintf ("%.0f.f,%.0f.f", min (ALTG, na.rm=TRUE), max (ALTG, na.rm=TRUE))
ncatt_put (newfile, "ALTG_SRTM", attname="actual_range", attval=minmax2) 
ncvar_put (newfile, "SFC_SRTM", SFC) 
ncvar_put (newfile, "ALTG_SRTM", ALTG) 
nc_close (newfile)
FigCap1 <- sprintf("The flight track for %s flight %s.", Project, Flight)

## ----plot-flight-track, fig.lp="fig:", fig.cap=FigCap1, include=TRUE-----

Z <- plotTrack (Data$LONC, Data$LATC, Data$Time, .Spacing=60, .WindFlags=2) 
title (Flight) 
FigCap2 <- sprintf ("The elevation of the terrain below the position of the aircraft during %s Flight %s.", Project, Flight)

## ----plot-terrain-height, echo=TRUE, include=TRUE, fig.lp="fig:", fig.cap=FigCap2, fig.height=5----

#SFC[is.na(SFC)] <- 0 
#r <- setRange(Data$Time, 82400,85200)
Z <- plotWAC (Data$Time, SFC, ylab="Terrain Elevation [m]") 
title (Flight)

## ----save-system-info, echo=FALSE----------------------------------------
cat (toLatex(sessionInfo()), file="SessionInfo")

## ----make-zip-archive, echo=TRUE, INCLUDE=TRUE---------------------------
system (sprintf("zip %s.zip %s.Rnw %s.pdf SessionInfo %s", thisFileName, 
                thisFileName, thisFileName, SaveRData))

