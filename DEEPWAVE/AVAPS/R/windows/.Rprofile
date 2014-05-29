# cat("sourcing /Users/postflight/.Rprofile\n")
library(eolsonde)

local({
    repos <- getOption("repos")
    repos <- c(repos,"http://www.eol.ucar.edu/software/R")
    options(repos=repos)

    if (getwd() != file.path(Sys.getenv("HOMEPATH"))) {
        rdata <- file.path(Sys.getenv("HOMEPATH"),".RData")
        if (file.exists(rdata))
            attach(rdata)
    }
})

if (existsFunction("project_init"))
    project_init()

