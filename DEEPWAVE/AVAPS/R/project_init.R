project_init <- function()
{
    options(time.zone="UTC")
    dpar(platform="NCAR AVAPS")

    if (.Platform$OS.type == "windows") {
        dpar(start="2014 may 1 00:00",lenday=180)
        Sys.setenv(PROJECT="DEEPWAVE")
        Sys.setenv(PLATFORM="AVAPS")
        Sys.setenv(SONDE_DATA="C:/avapsdata")
        # Sys.setenv(SONDE_DATA="F:/projects/MPEX/AVAPS/data")
    }
    else {
        Sys.setenv(SONDE_DATA="/net/isf/sounding.group/projects/MPEX/AVAPS/data/20130521_1011_RF99")
    }

    NULL
}
