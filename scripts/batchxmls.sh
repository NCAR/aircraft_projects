#!/bin/bash

#cd ${PROJ_DIR}/;
platform=$(uname)
echo $1
echo $2
echo $3
# Grep recursively (-r), Ignore binary files (-I), print file names for any
# exact match (-l) for the word "BESTVEL" in a subset of all the files
# determined by the find. The find searches all the regular files' names for 
# *.xml or *.xml*, ignoring dot files 
# tl;dr will search all xml's in the aircraft_projects subdirs for a keyword
# Places those names into temporary file batchxmllist.txt
fileNames=$(grep -rIl "$1" $(find . -type f \( -iname "*.xml*" -or -iname "*.xml" ! -iname ".*" \))) 
for xmlFile in $fileNames
do 
	echo "$xmlFile"
	if [[ $platform == "Linux" ]]; then
		echo "Linux, replacing $2 with $3 in file: $xmlFile "
		echo $(sed -i -z 's#'"${2}"'#'"${3}"'#g' $xmlFile)
		echo "Running ck_xml on $xmlFile"
		/opt/nidas/bin/ck_xml $xmlFile
		# |grep "Exception" to find errors and output 
	elif [[ $platform == "Darwin" ]]; then
		echo "Darwin, replacing $2 with $3 in file: $xmlFile "
	        echo "Can't perform ck_xml, check on linux system with nidas packages installed"
		# '' destructively overwrites original file
		echo $(sed -i '' 's#'"${2}"'#'"${3}"'#g' $xmlFile)
	else echo "Platform unhandled, check on a linux system with nidas
		packages installed."

	fi

done




# TODO:
# check replacement on Darwin
# simplify error consolodating on Linux 





Help()
{
   # Display Help
   echo "Wrapper scriot to easily batch edit xml files in directories below the
   location of the script."
   echo "Ideally perfect sed on one xml, then apply to many"
   echo
   echo "Usage: ./batchxmls.sh [-h|v] KeywordToIdentifyXMLs ToBeReplaced Replacement"
   echo 
   echo "Options:"
   echo "h     Print this Help."
   echo
   echo "Note: sed here is using # as a separator rather than / as xml
   formatting generally has the latter more than the former. Also to replace
   multipule lines, add a \ at the end to escape the implicit newline"
   echo
   echo
   echo
   echo "Readable example: ./batchxmls.sh 'GV Project' 'GV Project' 'TI3GER'"
   echo "Replace one line with many example:
   ./batchxmls.sh BESTVEL '<variable longname="Reference GPS number of satellites used in solution" name="GGNSAT" units="number"/>' '<variable longname="Reference GPS number of satellites tracked" name="GGNSATTRK" units="number"/>\'\n'          <variable longname="Reference GPS number of satellites used in solution" name="GGNSAT" units="number"/>\'\n'         <variable longname="Reference GPS number of satellites with L1/E1/B1 signals used in solution" name="GGNSATL1" units="number"/>\'\n'          <variable longname="Reference GPS number of satellites with multi-frequency signals used in solution" name="GGNSATMULTI" units="number"/>'
   "
}

# Get command line flags
while getopts ":h" option; do
   case $option in
      h) # call help function
         Help
         exit;;
   esac
done
