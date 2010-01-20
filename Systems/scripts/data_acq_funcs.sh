#!/bin/sh

# A set of scripts useful for starting and shutting down data acquistion.
# 
# The history of flights and hangar data acq periods for a project
# is kept in an XML file:
# $ADS3/projects/$PROJECT/$AIRCRAFT/nidas/flights.xml
#
# These functions use the proj_configs application to read
# and update that XML file.
# 
# These functions use kdialog to look almost GUI-like!
# 

#
# Create the stdout and stderr files used when running
# processes in these functions.
create_err_files() {
    local script=${1##*/}
    errfile=/tmp/$script.$$.err
    txtfile=/tmp/$script.$$.txt
    trap "{ rm -f $errfile $txtfile; };" EXIT
}

start_dcopserver() {
    if [ ! -f $HOME/.DCOPserver_`hostname`__0 ]; then
        # echo "dcopserver not running"
        dcopserver
    fi
}

check_env_vars() {
    # Check required environment variables.
    if [ -z "$LOCAL" -o -z "$PROJECT" -o -z "$AIRCRAFT" ]; then
        kdialog --caption "Environment Error" \
            --warningcontinuecancel "one of LOCAL, PROJECT or AIRCRAFT environment variables are not defined"
        exit 1
    fi
    [ -z "$PROJ_DIR" ] && export PROJ_DIR=$LOCAL/projects
}

set_config_dir() {
    # Use env vars for path to flights.xml and other nidas xml files
    # Don't expand the $PROJ_DIR variable yet
    # cfgdir is a global bash variable
    cfgdir=\$PROJ_DIR/$PROJECT/$AIRCRAFT/nidas
    local cdir=`eval echo $cfgdir`
    if [ ! -d $cdir ]; then
        kdialog --caption "Missing Folder" \
            --warningcontinuecancel "$cdir does not exist"
        exit 1
    fi
    cd $cdir
}

# look in current directory for all .xml files, ignoring one named
# flights.xml.  These should then be the nidas XML files.
get_nidas_xmls () {
    local -a xmls
    shopt -s nullglob
    for f in *.xml; do
        [ $f != flights.xml ] && xmls=(${xmls[@]} $f)
    done
    echo ${xmls[@]}
}

# List the flight names found in flights.xml
get_flights () {
    if proj_configs -n flights.xml > $txtfile 2> $errfile; then
        cat $txtfile
    else
        kdialog --caption "get_flights Error" \
            --warningcontinuecancel "`head -5 $errfile`"
        # $?: continue=0, cancel=2
        [ $? -eq 2 ] && return 1
    fi
}

# Return the last word passed to this function, useful
# for figuring out the last flight.
get_last () {
    local -a args=("$@")
    local i=$((${#args[*]}-1))
    [ $i -ge 0 ] && echo "${args[$i]}"
}

# From a string XXnn, where nn are digits, return the decimal value of nn
flight_number () {
    # read flight number. Put 10# in front so bash treats it as decimal
    echo $((`echo $1 | sed 's/^../10#/'`))
}

# From a flight number string XXmm, return XXnn, where nn = mm+1
next_flight () {
    if [ -n "$1" ]; then
        local n=$((`flight_number $1` + 1))
        echo $1 | awk -v n=$n '{printf "%s%02d",substr($1,1,2),n}'
    fi
}

# From a flight number string XXmm, return XXnn, where nn = mm-1
prev_flight () {
    if [ -n "$1" ]; then
        local n=$((`flight_number $1` - 1))
        echo $1 | awk -v n=$n '{printf "%s%02d",substr($1,1,2),n}'
    fi
}

# type of flight, tf, ff, rf, other something else
flight_type () {
    echo $1 | cut -c1-2
}

# type of configuration: flight or hangar
config_type () {
    case $1 in
    tf* | ff* | rf*)
        echo flight
    ;;
    *)
        echo hangar
    ;;
    esac
}

# get parameters (xml,begin,end) for a given configuration
get_config () {
    if proj_configs -g $1 flights.xml 2> $errfile | tail -1 > $txtfile; then
        # xmlname in $txtfile contains env variables
        # don't want to expand them, so use cat here
        cat $txtfile
    else
        kdialog --caption "get_config Error" \
            --warningcontinuecancel "`head -5 $errfile`"
        # $?: continue=0, cancel=2
        [ $? -eq 2 ] && return 1
    fi
}

# Display all current configurations, with associated xml file,
# and begin and end times
display_configs () {
    if true; then
        # --font -adobe-courier-medium-o-normal--18-180-75-100-m-110-iso8859-1 \
        kdialog --title "Sampling Periods for Project: $PROJECT (Click to Continue)" \
            --passivepopup \
                "`proj_configs -l -f flights.xml 2>&1 | sed s,$cfgdir/,,g`" 30
    else
        kdialog --caption "Data System Configurations" \
            --warningcontinuecancel \
                "`proj_configs -l -f flights.xml 2>&1 | sed s,$cfgdir/,,g`"
        # $?: continue=0, cancel=2
        [ $? -eq 2 ] && return 1
    fi
}

# Update the end time of a configuration if it is later than
# a given time, typically the current time.
terminate_config () {
    local tterm=$2
    local -a cfg=(`get_config $1`) || return 1
    local edate=${cfg[2]}
    if [ $edate -gt $tterm ]; then
        kdialog --title "Info: setting end time on $1" \
            --passivepopup \
            "Setting end time of $1 to `utime $tterm +'%Y %b %d %H:%M:%S'`, previous=`utime $edate +'%Y %m %d %H:%M:%S'`" 5
        if ! proj_configs -t $tterm flights.xml 2> $errfile; then
            kdialog --caption "terminate_config Error" \
                --warningcontinuecancel "`head -5 $errfile`"
            # $?: continue=0, cancel=2
            [ $? -eq 2 ] && return 1
        fi
    fi
}

terminate_last_config () {
    local -a cfgs=(`get_flights`) || exit 1

    # last config, could be empty, but shouldn't since we're supposed
    # to terminate it.
    local prevconfig=`get_last ${cfgs[@]}`

    if [ -z "$prevconfig" ]; then
        kdialog --caption "No Data Configuration" \
                --warningcontinuecancel "no data configurations found"
        # $?: continue=0, cancel=2
        [ $? -eq 2 ] && exit 1
    else
        tnow=`utime now`
        terminate_config $prevconfig $tnow || exit 1
    fi
}


# Extend the end time of a configuration
extend_config () {
    if ! proj_configs -t $1 flights.xml 2> $errfile; then
        kdialog --caption "extend_config Error" \
            --warningcontinuecancel "`head -5 $errfile`"
        # $?: continue=0, cancel=2
        [ $? -eq 2 ] && return 1
    fi
}

# for testing, pass bad option to proj_configs
generate_error () {
    if proj_configs -q $1 flights.xml > $txtfile 2> $errfile; then
        local -a cfg=($(<$txtfile))
        local n=${#cfg[@]}
        echo ${cfg[$(($n-3))]} ${cfg[$(($n-2))]} ${cfg[$(($n-1))]}
    else
        kdialog --caption "get_config Error" \
            --warningcontinuecancel "`head -5 $errfile`"
        # $?: continue=0, cancel=2
        [ $? -eq 2 ] && return 1
    fi
}

# Start dsm_server, create a kdialog progress bar, and do an infinite
# loop waiting until the kdialog progress bar is killed.
start_dsm_server() {
    local config=$1
    local xml=$2

     set -x

    if sudo -E /opt/local/nidas/x86/bin/dsm_server -r -u ads $xml 2>$errfile > $txtfile; then

        local pidfile=/tmp/dsm_server.pid
        local pid=""
        local ntry=10
        while [ $ntry -gt 0 ]; do
            if [ -f $pidfile ]; then
                pid=$(<$pidfile)
                [ -d /proc/"$pid" ] && break
            fi
            ntry=$(($ntry - 1))
            sleep 1
        done
        if [ $ntry -eq 0 ]; then
            kdialog --caption "dsm_server Is Not Starting" \
                --error "`head -10 $errfile`"
            exit 1
        fi

        totalflight=$((12 * 3600))
        kdialog --caption "dsm_server" \
            --progressbar "dsm_server, pid=$pid, config=$config. Progress is % of 12 hour flight. Press X or Cancel to shut down" $totalflight > /tmp/dsm_server.dcopRef
            # --geometry +10-10 \
        local dcopRef=$(</tmp/dsm_server.dcopRef)
        dcop $dcopRef showCancelButton true
        dcop $dcopRef setProgress 0
        # wait until canceled or process id disappears
        local seconds=0
        local nsec=2
        while true; do
            sleep $nsec
            # dcop fails if stop_dsm_server closes the progressbar
            # In which case we exit
            res=`dcop $dcopRef wasCancelled 2>/dev/null` || exit 1
            if [ $res == "true" ]; then
                stop_dsm_server
                terminate_last_config
                break
            fi
            if [ ! -d /proc/"$pid" ];then
                dcop $dcopRef close 2> /dev/null
                rm -f /tmp/dsm_server.dcopRef
                kdialog --caption "dsm_server Has Quit" \
                    --error "dsm_server, pid=$pid is not running"
                terminate_last_config
                exit 1
            fi
            seconds=$(($seconds + $nsec))
            if [ $(( $seconds % 60)) -eq 0 ]; then
                dcop $dcopRef setProgress $seconds
            fi
        done
    else
        kdialog --caption "dsm_server Failed" \
            --error "`head -10 $errfile`"
        exit 1
    fi
}

stop_dsm_server() {
    local pidfile=/tmp/dsm_server.pid

    if [ -f $pidfile ]; then
        local pid=$(<$pidfile)
        kdialog --caption "Shutdown dsm_server" --warningcontinuecancel \
            "Shutdown dsm_server (pid=$pid)?"
        # $?: continue=0, cancel=2
        stat=$?
        [ $stat -ne 0 ] && exit 1

        if [ -f /tmp/dsm_server.dcopRef ]; then
            local dcopRef=$(</tmp/dsm_server.dcopRef)
            dcop $dcopRef close 2> /dev/null
            rm -f /tmp/dsm_server.dcopRef
        fi
        ntry=0
        while [ -f $pidfile -a $ntry -lt 5 ]; do
            kill -TERM $pid 2> /dev/null || break
            ntry=$(($ntry + 1))
            sleep 2
        done
    fi

    if pgrep dsm_server > /dev/null; then
        pid=`pgrep dsm_server`
        kdialog --title "Kill dsm_server" \
                 --passivepopup \
            "dsm_server, pid=$pid is not shutting down cleanly, doing a kill -9" 5
        pkill -9 dsm_server
        # if dsm_server is not shut down cleanly, pid file may exist
        [ -f $pidfile ] && rm -f $pidfile
    fi
}

check_dsm_server() {
    local pidfile=/tmp/dsm_server.pid
    if [ -f $pidfile ]; then
        local pid=$(<$pidfile)
        if [ -n "$pid" -a -d /proc/"$pid" ];then
            echo 1
            return
        fi
    fi
    echo 0
}

