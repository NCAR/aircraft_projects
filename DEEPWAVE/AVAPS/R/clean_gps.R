

clean_gps <- function()
{
    set_sproject(project="DEEPWAVE",platform="AVAPS")

    sdataset("QC")

    t1 <- utime("2014 06 11 00:00")

    t2 <- utime("2014 07 21 00:00")

    outpath <- file.path("/scr/tmp/kbeierle",Sys.getenv("SPROJECT"),Sys.getenv("SDATASET"))

    if (!file.exists(outpath))
        dir.create(outpath,recursive=TRUE)


    for (tx in seq(from=t1,to=t2,by=86400*7)) {
        tx <- utime(tx)
        dpar(start=tx,lenday=7)

        sds <- readSoundings()

        for (n in names(sds)) {
            cat("sounding: ",n,"\n")

            sdx <- filter_gps(sds[[n]],vzdiff = 5, vhdiff = 5, maxvel = 200, maxdriftvel = 20, 
                        maxaccel = 5, nloop = 5) 

            outfile <- file.path(outpath,n)

            writeQCFile(sdx,outfile)
        }
    }
}
