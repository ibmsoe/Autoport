import re

class ResultParser:
    def MavenBuildSummary(self, logfilename):
        '''
            Creates a detailed result summary from a Maven build output file.

            use example for creating a JSON output:
                import json
                from resultParser import ResultParser
                p = ResultParser()
                r = p.MavenBuildSummary("mvn.Test.res.x86")
                s = json.dumps(r)
                f = open("out.json", "w")
                f.write(s)
                f.close()

            @param self the ResultParser object
            @param logfilename the maven build output file name
            @return a dictionary containing the results.
        '''
        f = open(logfilename)
        totals = { "total": 0, "failures": 0, "errors": 0,
                   "skipped": 0, "duration": 0 }
        results = {}
        projectResults = {}
        curProject = ""
        curClass = ""
        projectPattern = re.compile('\[INFO\] Building (.*)')
        classPattern = re.compile('Running (.*)')
        resultsPattern = re.compile('Tests run: (\d*), Failures: (\d*), Errors: (\d*), Skipped: (\d*), Time elapsed: (\d*\.\d*) sec[ \<\<\< FAILURE\!]?')

        for line in f.readlines():
            projectMatch = projectPattern.match(line)
            if projectMatch != None:
                # Append the previous project's results
                if len(projectResults) > 0 and projectResults["total"] != 0:
                    results[curProject] = projectResults
                    totals["total"] = totals["total"] + projectResults["total"]
                    totals["failures"] = totals["failures"] + projectResults["failures"]
                    totals["errors"] = totals["errors"] + projectResults["errors"]
                    totals["duration"] = totals["duration"] + projectResults["duration"]
                projectResults = {}
                projectResults["total"] = 0
                projectResults["failures"] = 0
                projectResults["errors"] = 0
                projectResults["skipped"] = 0
                projectResults["duration"] = 0
                curProject = projectMatch.group(1)
            else:
                classMatch = classPattern.match(line)
                if classMatch != None:
                    curClass = classMatch.group(1)
                    pass
                else:
                    resultMatch = resultsPattern.match(line)
                    if resultMatch != None:
                        projectResults[curClass] = {
                            "total": int(resultMatch.group(1)),
                            "failures": int(resultMatch.group(2)),
                            "errors": int(resultMatch.group(3)),
                            "skipped": int(resultMatch.group(4)),
                            "duration": float(resultMatch.group(5))
                        }
                        projectResults["total"] = projectResults["total"] + int(resultMatch.group(1))
                        projectResults["failures"] = projectResults["failures"] + int(resultMatch.group(2))
                        projectResults["errors"] = projectResults["errors"] + int(resultMatch.group(3))
                        projectResults["skipped"] = projectResults["skipped"] + int(resultMatch.group(4))
                        projectResults["duration"] = projectResults["duration"] + float(resultMatch.group(5))

        if len(projectResults) > 0 and projectResults["total"] != 0:
            results[curProject] = projectResults
            totals["total"] = totals["total"] + projectResults["total"]
            totals["failures"] = totals["failures"] + projectResults["failures"]
            totals["errors"] = totals["errors"] + projectResults["errors"]
            totals["duration"] = totals["duration"] + projectResults["duration"]
        f.close()
        totals["results"] = results
        return totals

    def MavenBuildCompare(self, leftName, left, rightName, right, only_diff = True):
        '''
            Compares the results of 2 different builds.
            @param self
            @param leftName the name to give to the results of the first result set
            @param left file name of the first maven result output
            @param rightName the name to give to the results of the second result set
            @param right file name of the second maven result output
            @param only_diff only output differencies between the 2 result sets
        '''
        # eventually remove these and take the result of MavenBuildSummary as an
        # input of MavenBuildCompare?
        left_r = self.MavenBuildSummary(left)
        right_r = self.MavenBuildSummary(right)

        res = {
                "total": { leftName: left_r["total"], rightName: right_r["total"] },
                "failures": { leftName: left_r["failures"], rightName: right_r["failures"] },
                "errors": { leftName: left_r["errors"], rightName: right_r["errors"] },
                "skipped": { leftName: left_r["skipped"], rightName: right_r["skipped"] },
                "duration": { leftName: left_r["duration"], rightName: right_r["duration"] },
                "results": {}
              }

        if (only_diff == True
          and res["total"][leftName] == res["total"][rightName]
          and res["failures"][leftName] == res["failures"][rightName]
          and res["errors"][leftName] == res["errors"][rightName]
          and res["skipped"][leftName] == res["errors"][rightName]):
            # Nothing more, since we know for sure there's no difference
            return res

        # For each test suite of left_r, look for the corresponding result in right_r
        for suite in left_r["results"].keys():
            for test in left_r["results"][suite].keys():
                if (test == "total"
                 or test == "failures"
                 or test == "errors"
                 or test == "skipped"
                 or test == "duration"):
                    continue # obviously not a test

                # check if the test exists in right_r
                if (right_r["results"].has_key(suite)
                 and right_r["results"][suite].has_key(test)):
                    if (only_diff == True
                     and left_r["results"][suite][test]["total"]
                      == right_r["results"][suite][test]["total"]
                     and left_r["results"][suite][test]["failures"]
                      == right_r["results"][suite][test]["failures"]
                     and left_r["results"][suite][test]["errors"]
                      == right_r["results"][suite][test]["errors"]
                     and left_r["results"][suite][test]["skipped"]
                      == right_r["results"][suite][test]["skipped"]):
                        # No difference, don't store this result
                        continue

                    if not res["results"].has_key(suite):
                        res["results"][suite] = {}
                    if not res["results"][suite].has_key(test):
                        res["results"][suite][test] = {
                            "total": { leftName: 0, rightName: 0 },
                            "failures": { leftName: 0, rightName: 0 },
                            "errors": { leftName: 0, rightName: 0 },
                            "skipped": { leftName: 0, rightName: 0 },
                            "duration": { leftName: 0, rightName: 0 }
                        }

                    # Put the results in the output
                    res["results"][suite][test]["total"][leftName] = left_r["results"][suite][test]["total"]
                    res["results"][suite][test]["total"][rightName] = right_r["results"][suite][test]["total"]
                    res["results"][suite][test]["failures"][leftName] = left_r["results"][suite][test]["failures"]
                    res["results"][suite][test]["failures"][rightName] = right_r["results"][suite][test]["failures"]
                    res["results"][suite][test]["errors"][leftName] = left_r["results"][suite][test]["errors"]
                    res["results"][suite][test]["errors"][rightName] = right_r["results"][suite][test]["errors"]
                    res["results"][suite][test]["skipped"][leftName] = left_r["results"][suite][test]["skipped"]
                    res["results"][suite][test]["skipped"][rightName] = right_r["results"][suite][test]["skipped"]
                    res["results"][suite][test]["duration"][leftName] = left_r["results"][suite][test]["duration"]
                    res["results"][suite][test]["duration"][rightName] = right_r["results"][suite][test]["duration"]
                else: # Nothing in the Right test
                    # Check we have things in res
                    if not res["results"].has_key(suite):
                        res["results"][suite] = {}
                    if not res["results"][suite].has_key(test):
                        res["results"][suite][test] = {
                            "total": { leftName: 0, rightName: 0 },
                            "failures": { leftName: 0, rightName: 0 },
                            "errors": { leftName: 0, rightName: 0 },
                            "skipped": { leftName: 0, rightName: 0 },
                            "duration": { leftName: 0, rightName: 0 }
                        }
                    
                    res["results"][suite][test]["total"][leftName] = left_r["results"][suite][test]["total"]
                    res["results"][suite][test]["total"][rightName] = 0
                    res["results"][suite][test]["failures"][leftName] = left_r["results"][suite][test]["failures"]
                    res["results"][suite][test]["failures"][rightName] = 0
                    res["results"][suite][test]["errors"][leftName] = left_r["results"][suite][test]["errors"]
                    res["results"][suite][test]["errors"][rightName] = 0
                    res["results"][suite][test]["skipped"][leftName] = left_r["results"][suite][test]["skipped"]
                    res["results"][suite][test]["skipped"][rightName] = 0
                    res["results"][suite][test]["duration"][leftName] = left_r["results"][suite][test]["duration"]
                    res["results"][suite][test]["duration"][rightName] = 0

        # Same, in the other way to add the eventually missing output on the left
        for suite in right_r["results"].keys():
            for test in right_r["results"][suite].keys():
                if (test == "total"
                 or test == "failures"
                 or test == "errors"
                 or test == "skipped"
                 or test == "duration"):
                    continue # obviously not a test

                # check if the test exists in left_r
                if (not left_r["results"].has_key(suite)
                 or not left_r["results"][suite].has_key(test)):
                    # Check we have things in res
                    if not res["results"].has_key(suite):
                        res["results"][suite] = {}
                    if not res["results"][suite].has_key(test):
                        res["results"][suite][test] = {
                            "total": { leftName: 0, rightName: 0 },
                            "failures": { leftName: 0, rightName: 0 },
                            "errors": { leftName: 0, rightName: 0 },
                            "skipped": { leftName: 0, rightName: 0 },
                            "duration": { leftName: 0, rightName: 0 }
                        }

                    res["results"][suite][test]["total"][rightName] = right_r["results"][suite][test]["total"]
                    res["results"][suite][test]["total"][leftName] = 0
                    res["results"][suite][test]["failures"][rightName] = right_r["results"][suite][test]["failures"]
                    res["results"][suite][test]["failures"][leftName] = 0
                    res["results"][suite][test]["errors"][rightName] = right_r["results"][suite][test]["errors"]
                    res["results"][suite][test]["errors"][leftName] = 0
                    res["results"][suite][test]["skipped"][rightName] = right_r["results"][suite][test]["skipped"]
                    res["results"][suite][test]["skipped"][leftName] = 0
                    res["results"][suite][test]["duration"][rightName] = right_r["results"][suite][test]["duration"]
                    res["results"][suite][test]["duration"][leftName] = 0

        return res

