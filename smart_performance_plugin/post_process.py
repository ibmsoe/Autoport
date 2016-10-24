#!/usr/bin/env python

#post_process.py: post processes smart plugin data and generates csv files
#Version: 1.2
#Copyright: IBM
#Author: Saurabh Gupta - sagupta6@in.ibm.com

import json
import sys
import re
import os.path

def check_files_exist(file_names):
  for file_name in file_names:
    if os.path.isfile(file_name):
      return
    print file_name, "does not exist or is not a file"
    sys.exit(1)

if len(sys.argv) != 3:
  print "Usage: post_process.py <input bz2 file> <target directory>"
  print "       input bz2 file: this is the file created by smart perf plugin"
  print "       target directory: this is the directory where generated csv files are kept"
  sys.exit(1)

bzip_file = sys.argv[1]
check_files_exist([bzip_file])

if bzip_file.endswith('.arti'):
  dir_prefix = bzip_file.replace('.tar.bz2.arti', "")
else:
  dir_prefix = bzip_file.replace('.tar.bz2', "")

data_file = os.path.split(dir_prefix)[1]
target_dir = sys.argv[2]

if not os.path.exists(target_dir):
  os.makedirs(target_dir)

os.system("tar jxf " + bzip_file + " -C " + target_dir)

dir_prefix = target_dir + "/" + data_file
if not os.path.exists(dir_prefix):
  print dir_prefix, "does not exist"
  sys.exit(1)

log_file = dir_prefix + "/" + "autoport_perf.log"
check_files_exist([log_file])
#dev_name = sys.argv[3]
duration = None
start_t = []
end_t = []
timer_duration = -1
date_duration = -1
with open(log_file, 'r') as logF:
  for line in logF:
    line = line.strip()
    start_match = re.search('Profilers start at:.*(\d+).*(\d\d):(\d\d):(\d\d)', str(line))
    if start_match:
      start_t.append(int(start_match.group(1)))
      start_t.append(int(start_match.group(2)))
      start_t.append(int(start_match.group(3)))
      start_t.append(int(start_match.group(4)))

    timer_match = re.search('TIMER stop:\s+(\d+)', str(line))
    if timer_match:
      timer_duration = long(timer_match.group(1))

    date_match = re.search('TIME_TAKEN:\s+(\d+)', str(line))
    if date_match:
      date_duration = long(date_match.group(1))

    end_match = re.search('Profilers stop at:.*(\d+).*(\d\d):(\d\d):(\d\d)', str(line))
    if end_match:
      end_t.append(int(end_match.group(1)))
      end_t.append(int(end_match.group(2)))
      end_t.append(int(end_match.group(3)))
      end_t.append(int(end_match.group(4)))

if date_duration == -1:
  duration = (end_t[0] - start_t[0]) * 24 * 3600 + (end_t[1] - start_t[1]) * 3600 + (end_t[2] - start_t[2]) * 60 + (end_t[3] - start_t[3])
else:
  duration = date_duration

if duration is None:
  print "Unable to extract duration from log file", log_file
  sys.exit(1)

data = {}
output_file = data_file + "." + "json"
data['time'] = {}
data['time']['duration'] = duration
data['time']['unit'] = 'seconds'
with open(output_file, 'w') as outfile:
    json.dump(data, outfile)
os.system("rm -Rf " + dir_prefix)
sys.exit(0)
