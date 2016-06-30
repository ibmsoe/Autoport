import ast
import urllib2
import base64
import sys
import globals

# Progress Bar Report
def determineProgress ():
    url = str(globals.jenkinsUrl)
    try:
        req = urllib2.Request(url + "/api/python?depth=1&tree=jobs[displayName,lastBuild[result]]")
        if globals.auth:
            auth_header = 'Basic ' + base64.encodestring('%s:%s' % (globals.configJenkinsUsername, globals.configJenkinsPassword))[:-1]
            req.add_header('Authorization', auth_header)
        response = urllib2.urlopen(req)
        xml_input_no_filter = ast.literal_eval(response.read())
        all_jobs = xml_input_no_filter['jobs']
    except IOError as e:
        assert(False), "Please provide valid jenkins url"

    success = 0
    unstable = 0
    failure = 0
    aborted = 0
    # projects that have never been built or are in the process of being built
    neverBeenBuilt = 0
    progressResults = [neverBeenBuilt, failure, unstable, success, aborted]

    for row in all_jobs:
        if   row['lastBuild'] == None:
            progressResults[0] += 1
        elif row['lastBuild']['result'] == None:
            progressResults[0] += 1
        elif row['lastBuild']['result'] == 'FAILURE':
            progressResults[1] += 1
        elif row['lastBuild']['result'] == 'UNSTABLE':
            progressResults[2] += 1
        elif row['lastBuild']['result'] == 'SUCCESS':
            progressResults[3] += 1
        elif row['lastBuild']['result'] == 'ABORTED':
            progressResults[4] += 1
        else:
            print "Unknown Status Encountered " + str(row['lastBuild'])

    total = 0
    for status in progressResults:
        total += status

    neverBeenBuiltP = progressResults[0] * 100 / total
    failureP = progressResults[1] * 100 / total
    unstableP = progressResults[2] * 100 / total
    successP = progressResults[3] * 100 / total
    abortedP = progressResults[4] * 100 / total

    percentages = [neverBeenBuiltP, failureP, unstableP, successP, abortedP]

    results = [progressResults, percentages]

    return results
