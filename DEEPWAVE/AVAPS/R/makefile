FUN=sproject_init.R clean_gps.R

OFUN=$(FUN:%.R=.%.Ro)
all: $(OFUN)

.%.Ro : %.R
	R --no-readline --vanilla --slave --restore --save -e "source('$<')" && touch $@

clean:
	$(RM) $(OFUN) .RData
