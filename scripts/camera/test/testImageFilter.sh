#THIS NEEDS WORK

# Standard camera images - test2 is dir of sample camera images
./Image_Filter.pl test2

# Satellite images - test is dir of sample satellite images
./Image_Filter.pl test -pattern:none "-maxdev:60|60|60"

# Note, if you wanted to check time continuity on satellite, you could use the following command, but in the test case
# will complain that there are duplicate images at the same time (ch1 and ch4). This command is looking for a  30 min 
# gap = 1800 secs.  Note: code will try to do ground check and skip it.
./Image_Filter.pl test -pattern:'ops.goes-12.20(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)().*\.jpg' "-maxdev:60|60|60" -t:1800
