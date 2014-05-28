library(eolsonde)

# cat("sourcing /Users/postflight/.Rprofile\n")
local({
    repos <- getOption("repos")
    repos <- c(repos,"http://www.eol.ucar.edu/software/R")
    options(repos=repos)

    rdata <- file.path(Sys.getenv("HOMEPATH"),".RData")
    if (file.exists(rdata))
        attach(rdata)
})



if (existsFunction("project_init"))
    project_init()

# updateEOL <- function()
# {
#     update.packages(oldPkgs=c("eolts","isfs","eolsonde"),repos="http://www.eol.ucar.edu/software/R")
# }
# cat("Do: updateEOL() to update the eolts, isfs and eolsdng packages\n")
