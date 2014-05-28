
FUN=project_init.R project_plots.R

OFUN=$(FUN:%.R=.%.Ro)
all: $(OFUN)

.%.Ro : %.R
	R --no-readline --vanilla --slave --restore --save -e "source('$<')" && touch $@

clean:
	$(RM) $(OFUN) .RData
