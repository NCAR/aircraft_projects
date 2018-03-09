#!/bin/csh

cd ${RAW_DATA_DIR}/SOCRATES/GNI/logs
rm *exposure_times

foreach dir ([RTF]F??_*)
    echo $dir
    touch ../$dir.exposure_times
    foreach file ($dir/gni_server*log)
        echo $file
        /net/work/dev/jaa/gni/scripts/logs/get_exposure_times $file >> $dir.exposure_times
    end
end
