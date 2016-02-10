#!/bin/bash

cd /home/jenkins/jenkins_home/jobs/
NumFiles=`ls | wc -l`

echo "Current directory: $PWD"
echo "Number of files in current directory: $NumFiles"
echo ""
echo "Remove all but the most recent 2000 Jenkins Jobs [y/Y]"

read -n 1 user_input

if [ $user_input == "y" ] || [ $user_input == "Y" ]; then
    echo "Removing files ..."
    rm -rf `ls -t | awk 'NR>2000'`
    echo "Please use the Jenkins dashboard to reload the disk configuration"
fi
