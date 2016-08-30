Usage:  
$ ./basic_perf_plugin.sh cmd="workload command" workload="xyz" department_name="your department name"  
$ ls  
basic_perf_data.ubuntu-saurabh.default.2016-04-14_0559.tar.bz2  
basic_perf_plugin.sh  
$  

Substitute xyz above with the workload name.  
To use perf pass the following argument in addition to above:  
extra_profilers="perf"  
  
Note: perf, when enabled, is enabled to run after 60 seconds and  
for 60 seconds by default. To change the perf wait time and run time  
use perf_wait and perf_sleep time respectively   
e.g.  
$ ./basic_perf_plugin.sh cmd="workload cmd" extra_profilers="perf" perf_wait=30 perf_sleep=90  
    
The performance data is collected and bundled as a bz2 file as shown above.  
scp/sftp this file to the management server.  
  
Management server details:  
perf105127.aus.stglabs.ibm.com [ perf / perf123 ]  
Dir(s): /smart_perf_data/[environment]/[workload name]  

NB: basic_perf_plugin.sh is being developed by making changes (additions/reductions/modifications) to lpcpu.sh followed by a rename.
