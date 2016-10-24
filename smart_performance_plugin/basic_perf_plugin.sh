#!/bin/bash

#
# LPCPU (Linux Performance Customer Profiler Utility): ./lpcpu.sh
#
# (C) Copyright IBM Corp. 2015
#
# This file is subject to the terms and conditions of the Eclipse
# Public License.  See the file LICENSE.TXT in the main directory of the
# distribution for more details.
#

# since this plugin is being built on lpcpu hence the license implication

VERSION_STRING="v1.1 June 16 2016"

# how to call perf
PERF=$(which perf)

#duration for which perf runs
perf_sleep="60"
#duration for which perf waits
perf_wait="60"


# The following are the default profilers to use
profilers="iostat iostatx mpstat vmstat top" 
extra_profilers=""

# Duration of the profiler run, in seconds.
duration=120

# where to create the output data (a compressed tar ball)
output_dir=`pwd`

# optional directory name to use in the output_dir, otherwise defaults to AUTOPORT_PERF naming scheme
dir_name=""

# Duration between profiler samples (does not apply to some profilers)
interval=5

# should the resulting data be packaged into a compress tarball or left alone.  valid values are "yes" or "no"
package_results="yes"

# A command to run, if this is specified then the command is run and profiled from start
# to finish instead of profiling for the length of $duration
cmd=""

# Alternatively, a docker container to run and profile.
container=""

# Options for docker run. Helpful if you want to put a container in a cgroup
docker_run_opts=""


# no reason to modify this unless you know what you are doing
id="default"
RUN_NUMBER="001"


################################################
# 
# perf specific parameters

# Use callgraph on oprofile or perf
callgraph="no"

# control the frequency at which perf samples are collected
perf_frequency=""

# default to all cpus
perf_cpu=""

## argument import loop ############################################################################
# This loop takes the command line input variable (CLI) and sets the bash script variables
startup_output_log=""
for arg; do
    export "$arg"
    startup_output_log="${startup_output_log}Importing CLI variable : $arg\n"
done

profilers="$profilers $extra_profilers"

if [ -z "${workload}" ]; then
   echo "Error: workload name not specified"
   exit 1
fi
if [ -z "${department_name}" ]; then
   echo "Error: Department name not specified"
   exit 1
fi
# Location to store output data.
NAME=$(hostname -s)
TODAY=$(date +"%F_%H%M")
TAR_SUFFIX="tar.bz2"

if [ "$workload" = "autoport" ]; then
   if [ -z "${package}" ]; then
      echo "package not specified"
      exit 1
   fi
   dir_name=${package}.$TODAY
   TAR_SUFFIX=${TAR_SUFFIX}.arti
fi
if [ -z "${dir_name}" ]; then
    LOGDIR_NAME=basic_perf_data.$NAME.$id.$TODAY
else
    LOGDIR_NAME=${dir_name}
fi
LOGDIR=$output_dir/$LOGDIR_NAME
mkdir -p $LOGDIR
echo "$startup_output_log"  >> ${LOGDIR}/autoport_perf.log

OS=$(grep -w ID /etc/os-release|cut -d '=' -f 2| tr -d '"')

## utility functions ###############################################################################


## iostat ##########################################################################################
function setup_iostat() {
	echo "Setting up iostat." >> ${LOGDIR}/autoport_perf.log
	IOSTAT=$(which iostat)
	if [ -z "$IOSTAT" ]; then
		echo "ERROR: iostat is not installed.  To correct this problem install the sysstat package for your distribution."
		exit 1
	fi
}

function start_iostat() {
	echo "starting iostat -t $interval" >> ${LOGDIR}/autoport_perf.log
	iostat -t $interval > $LOGDIR/iostat.$id.$RUN_NUMBER &
	IOSTAT_PID=$!
	disown $IOSTAT_PID
}

function stop_iostat() {
	echo "Stopping iostat." >> ${LOGDIR}/autoport_perf.log
	kill $IOSTAT_PID
}

function report_iostat() {
	echo "Processing iostat data." >> ${LOGDIR}/autoport_perf.log
}
## iostatx ##########################################################################################
function setup_iostatx() {
        echo "Setting up iostat." >> ${LOGDIR}/autoport_perf.log
        IOSTAT=$(which iostat)
        if [ -z "$IOSTAT" ]; then
                echo "ERROR: iostat is not installed.  To correct this problem install the sysstat package for your distribution."
                exit 1
        fi
}

function start_iostatx() {
        echo "starting iostat -t -dcNx $interval" >> ${LOGDIR}/autoport_perf.log
        iostat -t -x $interval > $LOGDIR/iostatx.$id.$RUN_NUMBER &
        IOSTATX_PID=$!
        disown $IOSTATX_PID
}

function stop_iostatx() {
        echo "Stopping iostat." >> ${LOGDIR}/autoport_perf.log
        kill $IOSTATX_PID
}

function report_iostatx() {
        echo "Processing iostat data." >> ${LOGDIR}/autoport_perf.log
}


## OPERF##########################################################################################
function setup_operf() {
        echo "Setting up operf" >> ${LOGDIR}/autoport_perf.log
        OPERF=$(which operf)
        if [ -z "$OPERF" ]; then
                echo "ERROR: operf is not installed."
                exit 1
        fi
	echo $profilers | grep perf> /dev/null
	if [  $? == 0 ]; then
		echo "ERROR: perf and operf can not run at same time."
        	exit 1
    	fi
}

function start_operf() {
        echo "starting operf -s --session-dir $LOGDIR" >> ${LOGDIR}/autoport_perf.log
        operf -s --session-dir $LOGDIR > $LOGDIR/operf.$id.$RUN_NUMBER 2>&1 &
        OPERF_PID=$!
        disown $OPERF_PID
}

function stop_operf() {
        echo "Stopping operf" >> ${LOGDIR}/autoport_perf.log
    	kill -SIGINT $OPERF_PID
}

function report_operf() {
        echo "Processing operf data." >> ${LOGDIR}/autoport_perf.log
	opreport --session-dir $LOGDIR > $LOGDIR/operf_report.$RUN_NUMBER 2>&1
}


## vmstat ##########################################################################################
function setup_vmstat() {
	echo "Setting up vmstat." >> ${LOGDIR}/autoport_perf.log
	VMSTAT=$(which vmstat)
	if [ -z "$VMSTAT" ]; then
		echo "ERROR: vmstat is not installed."
		exit 1
	fi
}

function start_vmstat() {
	echo "starting vmstat."$id" ["$interval"]" >> ${LOGDIR}/autoport_perf.log
	vmstat_cmd="vmstat -t $interval"
	$vmstat_cmd  > $LOGDIR/vmstat.$id.$RUN_NUMBER &
	VMSTAT_PID=$!
	disown $VMSTAT_PID
}

function stop_vmstat() {
	echo "Stopping vmstat." >> ${LOGDIR}/autoport_perf.log
	kill $VMSTAT_PID
}

function report_vmstat() {
	echo "Processing vmstat data." >> ${LOGDIR}/autoport_perf.log
}


## top #############################################################################################
function setup_top() {
	echo "Setting up top." >> ${LOGDIR}/autoport_perf.log
	TOP=$(which top)
	if [ -z "$TOP" ]; then
		echo "ERROR: top is not installed."
		exit 1
	fi
}

function start_top() {
	echo "Starting top." >> ${LOGDIR}/autoport_perf.log
	top -b -d $interval -H > $LOGDIR/top.$id.$RUN_NUMBER &
	TOP_PID=$!
	disown $TOP_PID
}

function stop_top() {
	echo "Stopping top." >> ${LOGDIR}/autoport_perf.log
	kill $TOP_PID
}

function report_top() {
	echo "Processing top data." >> ${LOGDIR}/autoport_perf.log
}


## mpstat ##########################################################################################
function setup_mpstat() {
	echo "Setting up mpstat." >> ${LOGDIR}/autoport_perf.log
	MPSTAT=$(which mpstat)
	if [ -z "$MPSTAT" ]; then
		echo "ERROR: mpstat is not installed.  To correct this problem install the sysstat package for your distribution."
		exit 1
	fi
}

function start_mpstat() {
	echo "starting mpstat.$id ["$interval"]" >> ${LOGDIR}/autoport_perf.log
	mpstat -P ALL $interval > $LOGDIR/mpstat.$id.$RUN_NUMBER &
	MPSTAT_PID=$!
	disown $MPSTAT_PID
}

function stop_mpstat() {
	echo "Stopping mpstat." >> ${LOGDIR}/autoport_perf.log
	kill $MPSTAT_PID
}

function report_mpstat() {
	echo "Processing mpstat data." >> ${LOGDIR}/autoport_perf.log
}

## perf ##########################################################################################
function setup_perf() {
	echo "Setting up perf." >> ${LOGDIR}/autoport_perf.log
	if [ -z "$PERF" ]; then
        	echo "ERROR: perf is not installed."
	        exit 1
	fi
	echo $profilers | grep operf> /dev/null
	if [  $? == 0 ]; then
		echo "ERROR: perf and operf can not run at same time."
        	exit 1
    	fi

}

function start_perf() {
	local perf_cmd

	echo "starting perf" >> ${LOGDIR}/autoport_perf.log 
        perf_cpu_arg="-a -g -e cycles"
        if [ -n "$perf_cpu" ]; then
	        perf_cpu_arg="--cpu=$perf_cpu"
        fi
        perf_cmd="$PERF record $perf_cpu_arg -o $LOGDIR/perf_data.$RUN_NUMBER sleep $perf_sleep"
	if [ "$callgraph" = "yes" ]; then
		perf_cmd="$perf_cmd -g"
		echo "perf using callgraph" >> ${LOGDIR}/autoport_perf.log
	fi
	if [ -n "$perf_frequency" ]; then
		perf_cmd="$perf_cmd -F $perf_frequency"
		echo "perf using user specified frequency of [$perf_frequency]" >> ${LOGDIR}/autoport_perf.log 
	fi

	echo "sleeping for $perf_wait seconds before perf" >> ${LOGDIR}/autoport_perf.log 
  sleep $perf_wait
	echo "using perf command [$perf_cmd]" >> ${LOGDIR}/autoport_perf.log 
	$perf_cmd > $LOGDIR/perf.$id.$RUN_NUMBER 2>&1 &
  PERF_PID=$!
	disown $PERF_PID
}

function stop_perf() {
    	echo "Stopping perf." >> ${LOGDIR}/autoport_perf.log
    	#kill -SIGINT $PERF_PID
}

function report_perf() {
  echo "Processing perf data." >> ${LOGDIR}/autoport_perf.log
  if [ -n "$cont" ]; then
    # we're profiling a container
    # we want to find their root file system so we can see their symbols
    # we want the container, *not* the image, because we want to be able
    # to pick up the pid map files in /tmp that jits like hhvm and pypy emit.
    # however the mount seems to go away when the container closes so
    # leave this for now and go with the image
    image_dir=$(docker inspect $cont | grep LowerDir | egrep -o '[/a-z0-9]+/root')
    PERF_ARGS="--symfs=$image_dir"
  fi
  if [ "$callgraph" = "yes" ]; then
		sleep 5 #Wait for perf record to be terminated
		$PERF report -n -g flat,100 $PERF_ARGS -i $LOGDIR/perf_data.$RUN_NUMBER > $LOGDIR/perf_report.$RUN_NUMBER
		$PERF report -n -g $PERF_ARGS -i $LOGDIR/perf_data.$RUN_NUMBER > $LOGDIR/perf_report-callgraph.$RUN_NUMBER
	else
		sleep 5 #Wait for perf record to be terminated
		$PERF report --no-children $PERF_ARGS -i $LOGDIR/perf_data.$RUN_NUMBER > $LOGDIR/perf_report.$RUN_NUMBER 2>&1
		$PERF annotate $PERF_ARGS -i $LOGDIR/perf_data.$RUN_NUMBER > $LOGDIR/perf_annotate.$RUN_NUMBER 2>&1
	fi
}

## Generic Functions ###############################################################################

# in normal SIGINT handling just log the signal and exit
function sigint_normal_trap() {
    echo -e "\n\nCaught SIGINT --> exiting\n"
    exit 1
}

# when the profilers are running and a SIGINT is received we log the
# SIGNAL but continue running to allow the profilers to be cleanly
# shutdown
# NOTE: This means that when profilers are running and a SIGINT is
# received the script continues to run
function sigint_running_trap() {
    echo -e "\n\nCaught SIGINT --> stopping data collection\n"
}

####################################################################################################

# main block, used to log all output
{
    trap sigint_normal_trap SIGINT

    #echo "Running Autoport Performance Profiler Utility version $VERSION_STRING"
    echo "Running Autoport Performance Profiler Utility"  >> ${LOGDIR}/autoport_perf.log
    echo "$VERSION_STRING" > $LOGDIR/autoport_perf.version

    AUTOPORT_PERFDIR=`dirname $0`

    # dump the startup output log, doing it here so that is recorded
    echo -e "$startup_output_log" >> ${LOGDIR}/autoport_perf.log

    echo "Starting Time: `date`"  >> ${LOGDIR}/autoport_perf.log

    # Setup all profilers.
    for prof in $profilers; do
	setup_$prof
    done

    cat /proc/net/netstat > $LOGDIR/netstat.before 2>&1 
    netstat -s > $LOGDIR/netstat-s.before 2>&1 
    netstat -ta > $LOGDIR/netstat-ta.before 2>&1 
    netstat -i > $LOGDIR/netstat-i.before 2>&1 
    cat /proc/interrupts > $LOGDIR/interrupts.before 2>&1  
    cat /proc/meminfo > $LOGDIR/meminfo.before 2>&1  
    df -a > $LOGDIR/df.before 2>&1  
    ip -s link > $LOGDIR/ip-statistics.before 2>&1  
    ifconfig -a > $LOGDIR/ifconfig.before 2>&1  

    cat /proc/schedstat > $LOGDIR/schedstat.before 2>&1 
    cat /proc/slabinfo > $LOGDIR/slabinfo.before 2>&1 
    cat /proc/buddyinfo > $LOGDIR/buddyinfo.before 2>&1 

    trap sigint_running_trap SIGINT

    # Start all profilers.
    echo "Profilers start at: `date`" >> ${LOGDIR}/autoport_perf.log
    echo "TIMER start:" >> ${LOGDIR}/autoport_perf.log
    SECONDS=0
    start_time=$(date +%s)
    for prof in $profilers; do
	start_$prof
    done

    if [ -n "$container" ]; then
        # There is a race condition here where you will often lose the first
        # little bit of the output between run and attach.
        # However, docker logs grabs it all, so the resulting docker.STDOUT
        # and docker.STDERR files should be complete
        echo "Executing container '$container'" >> ${LOGDIR}/autoport_perf.log
	cont=$(docker run -d --net=none $docker_run_opts $container)
	echo "Container ID is $cont" >> ${LOGDIR}/autoport_perf.log
        WAIT="docker attach --no-stdin $cont"
	KILL="docker kill $cont"
    elif [ -n "$cmd" ]; then
	echo "Executing '$cmd'" >> ${LOGDIR}/autoport_perf.log
	if [ "$workload" = "autoport" ]; then
		eval $cmd &
	else
		$cmd &
	fi
	MAIN_WAIT_PID=$!
	WAIT="wait $MAIN_WAIT_PID"
	KILL="kill $MAIN_WAIT_PID"
    else
	echo "Waiting for $duration seconds." >> ${LOGDIR}/autoport_perf.log
	sleep $duration &
	MAIN_WAIT_PID=$!
	WAIT="wait $MAIN_WAIT_PID"
	KILL="kill $MAIN_WAIT_PID"
    fi
    # by waiting on the PID we get proper signal delivery to the
    # script which is necessary for the SIGINT handler to function
    # properly, if a signal (SIGINT) is received the wait will exit
    # prematurely
    $WAIT
    WAIT_RET_VAL=$?    
    echo "$WAIT_RET_VAL" > cmd_status

    # if the wait returned a non-zero value it may be because it was short-circuited by a SIGINT
    # if so, kill the PID we were waiting on because it will still be running, just in case
    if [ ${WAIT_RET_VAL} != 0 ]; then
        $KILL
    fi

    # Stop all profilers.
    for prof in $profilers; do
	stop_$prof
    done
    end_time=$(date +%s)
    seconds_duration=$SECONDS
    echo "Profilers stop at: `date`" >> ${LOGDIR}/autoport_perf.log
    echo "TIMER stop: $seconds_duration" >> ${LOGDIR}/autoport_perf.log
    echo "TIME_TAKEN: $(($end_time-$start_time))" >> ${LOGDIR}/autoport_perf.log

    trap sigint_normal_trap SIGINT

    cat /proc/net/netstat > $LOGDIR/netstat.after 2>&1 
    netstat -s > $LOGDIR/netstat-s.after 2>&1 
    netstat -ta > $LOGDIR/netstat-ta.after 2>&1 
    netstat -i > $LOGDIR/netstat-i.after 2>&1 
    cat /proc/interrupts > $LOGDIR/interrupts.after 2>&1 
    cat /proc/meminfo > $LOGDIR/meminfo.after 2>&1 
    df -a > $LOGDIR/df.after 2>&1 
    ip -s link > $LOGDIR/ip-statistics.after 2>&1 
    ifconfig -a > $LOGDIR/ifconfig.after 2>&1   

    cat /proc/schedstat > $LOGDIR/schedstat.after 2>&1 
    cat /proc/slabinfo > $LOGDIR/slabinfo.after 2>&1 
    cat /proc/buddyinfo > $LOGDIR/buddyinfo.after 2>&1 

    # Collect data for all profilers.
    for prof in $profilers; do
	report_$prof
    done

    # capture data
    echo "Gathering system information" >> ${LOGDIR}/autoport_perf.log
    dmesg > $LOGDIR/dmesg.STDOUT 2> $LOGDIR/dmesg.STDERR
    dmidecode > $LOGDIR/dmidecode.STDOUT 2> $LOGDIR/dmidecode.STDERR
    sysctl -a > $LOGDIR/sysctl.STDOUT 2> $LOGDIR/sysctl.STDERR 
    ulimit -a > $LOGDIR/ulimit.STDOUT 2> $LOGDIR/ulimit.STDERR 
    lspci -vv > $LOGDIR/lspci.STDOUT 2> $LOGDIR/lspci.STDERR 
    lspci -tv > $LOGDIR/lspci-tree.STDOUT 2> $LOGDIR/lspci-tree.STDERR 
    lsblk -f -t -m > $LOGDIR/lsblk.STDOUT 2> $LOGDIR/lsblk.STDERR 
    mount > $LOGDIR/mount.STDOUT 2> $LOGDIR/mount.STDERR 
    lscpu > $LOGDIR/lscpu.STDOUT 2> $LOGDIR/lscpu.STDERR	
    lscpu -a -e >> $LOGDIR/lscpu.STDOUT 2>> $LOGDIR/lscpu.STDERR 
    uname -a > $LOGDIR/uname.STDOUT 2> $LOGDIR/uname.STDERR 
    lsmod > $LOGDIR/lsmod.STDOUT 2> $LOGDIR/lsmod.STDERR 
    numactl --hardware > $LOGDIR/numactl.STDOUT 2> $LOGDIR/numactl.STDERR 
    ps -eL -o user=UID -o pid,ppid,lwp,c,nlwp,stime,sgi_p=CPU,time,cmd > $LOGDIR/ps.eLf.STDOUT 2> $LOGDIR/ps.eLf.STDERR 
    pstree -a -A -l -n -p -u > $LOGDIR/pstree.STDOUT 2> $LOGDIR/pstree.STDERR 
    ip addr > $LOGDIR/ip-addr.STDOUT 2> $LOGDIR/ip-addr.STDERR 
    brctl show > $LOGDIR/brctl-show.STDOUT 2> $LOGDIR/brctl-show.STDERR 
    if which rpm &> /dev/null; then
	rpm -qa | sort > $LOGDIR/rpm-qa.STDOUT 2> $LOGDIR/rpm-qa.STDERR 
    fi
    if which docker &> /dev/null; then
        docker info > $LOGDIR/docker-info.STDOUT 2> $LOGDIR/docker-info.STDERR
    fi

    # for some reason the +fg flag fails on some system, even though the man
    # page documentation implies that it should work.  if it does fail, just
    # run lsof without any flags so that we get some data
    if ! lsof +fg > $LOGDIR/lsof.fg.STDOUT 2> $LOGDIR/lsof.fg.STDERR; then
	lsof > $LOGDIR/lsof.STDOUT 2> $LOGDIR/lsof.STDERR 
    fi

    if [ -e /etc/redhat-release ]; then
        cp -a /etc/redhat-release $LOGDIR
    fi

    if [ -e /etc/SuSE-release ]; then
        cp -a /etc/SuSE-release $LOGDIR
    fi

    if [ -e /etc/os-release ]; then
        cp /etc/os-release $LOGDIR
    fi


    ARCH=`uname -m`
    if [ "$ARCH" == "ppc64" ]; then
       if which ppc64_cpu > /dev/null 2>&1; then
           ppc64_cpu --cores-present     >  $LOGDIR/ppc64_cpu 2>&1 
       fi
    fi
    cat /proc/version > $LOGDIR/version.STDOUT 2> $LOGDIR/version.STDERR 
    cat /proc/partitions > $LOGDIR/partitions.STDOUT 2> $LOGDIR/partitions.STDERR 
    cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor > $LOGDIR/scaling_governer.STDOUT 2> $LOGDIR/scaling_governer.STDERR 
    cat /sys/kernel/debug/sched_features > $LOGDIR/sched_features.STDOUT 2> $LOGDIR/sched_features.STDERR 
    cat /sys/devices/system/clocksource/clocksource0/current_clocksource > $LOGDIR/current_clocksource.STDOUT 2> $LOGDIR/current_clocksource.STDERR
    cat /proc/cmdline > $LOGDIR/cmdline.STDOUT 2> $LOGDIR/cmdline.STDERR
    cat /proc/cpuinfo > $LOGDIR/cpuinfo.STDOUT 2> $LOGDIR/cpuinfo.STDERR
    cat /proc/modules > $LOGDIR/modules.STDOUT 2> $LOGDIR/modules.STDERR
    gcc --version > $LOGDIR/gcc.STDOUT 2> $LOGDIR/gcc.STDERR
    ld -v > $LOGDIR/ld.STDOUT 2> $LOGDIR/ld.STDERR
    lvmdiskscan > $LOGDIR/lvmdiskscan.STDOUT 2> $LOGDIR/lvmdiskscan.STDERR

    # Lastly, grab logs and clean up the docker container if it exists.
    # We do this after data collection so we can get data out of it
    # after we stop it.
    if [ -n "$cont" ]; then
        docker logs $cont >${LOGDIR}/docker.STDOUT 2>${LOGDIR}/docker.STDERR
        docker rm -f $cont
    fi

    echo "Finishing time: `date`"  >> ${LOGDIR}/autoport_perf.log
} 2>&1 | tee -i ${LOGDIR}/autoport_perf.out
# without the -i option to tee the SIGINT handlers defined above do
# not function properly since tee will exit prematurely

if [ ${PIPESTATUS[0]} == 0 ]; then
    if [ "${package_results}" == "yes" ]; then
	echo -n "Packaging data..." >> ${LOGDIR}/autoport_perf.log
	pushd $output_dir > /dev/null
	if tar cjf ${LOGDIR_NAME}.${TAR_SUFFIX} $LOGDIR_NAME; then
	    echo "data collected is in ${LOGDIR}.tar.bz2"  >> ${LOGDIR}/autoport_perf.log
	    rm -Rf $LOGDIR
	else
	    echo "error packaging data.  Data is in $LOGDIR" | tee -a  ${LOGDIR}/autoport_perf.log
	fi
	popd > /dev/null
    else
	echo "Autoport Performance Profiler Utility has successfully completed.  Your data is available at ${LOGDIR}"  >> ${LOGDIR}/autoport_perf.log
    fi
else
    echo "ERROR: Autoport Performance Profiler Utility has encountered an error.  Your data is available at ${LOGDIR}"  >> ${LOGDIR}/autoport_perf.log
    exit 1
fi
