sproject_init <- function()
{
    options(time.zone="UTC")
    dpar(platform="NCAR AVAPS")

    dpar(start="2014 may 1 00:00",lenday=180)
    if (.Platform$OS.type == "windows") {
        Sys.setenv(PROJECT="DEEPWAVE")
        Sys.setenv(PLATFORM="AVAPS")
        Sys.setenv(SONDE_DATA="C:/avapsdata")
        # Sys.setenv(SONDE_DATA="F:/projects/MPEX/AVAPS/data")
    }

    NULL
}
