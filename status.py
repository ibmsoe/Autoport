import ast
import urllib
import sys
import globals

# Progress Bar Report
def determineProgress ():
    url = str(globals.jenkinsUrl)
    xml_input_no_filter = ast.literal_eval(urllib.urlopen(url + "/api/python?depth=1&tree=jobs[displayName,lastBuild[result]]").read())
    all_jobs = xml_input_no_filter['jobs']

    success = 0
    unstable = 0
    failure = 0
    # projects that have never been built or are in the process of being built
    neverBeenBuilt = 0
    progressResults = [neverBeenBuilt, failure, unstable, success]

    for row in all_jobs:
        if   row['lastBuild'] == None:
            progressResults[0] += 1
        elif row['lastBuild']['result'] == 'FAILURE':
            progressResults[1] += 1
        elif row['lastBuild']['result'] == 'UNSTABLE':
            progressResults[2] += 1
        elif row['lastBuild']['result'] == 'SUCCESS':
            progressResults[3] += 1
        else:
            print "Unknown Status Encountered"

    total = 0
    for status in progressResults:
        total += status

    neverBeenBuiltP = progressResults[0] * 100 / total
    failureP = progressResults[1] * 100 / total
    unstableP = progressResults[2] * 100 / total
    successP = progressResults[3] * 100 / total

    percentages = [neverBeenBuiltP, failureP, unstableP, successP]

    return percentages