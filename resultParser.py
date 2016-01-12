import re
import codecs
import json
import diff_match_patch
import logdiffutil
from log import logger

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
        resultsPattern = re.compile('Tests run: (\d*), Failures: (\d*), Errors: (\d*), Skipped: (\d*), Time elapsed: (\d*\.?\d*) sec[ \<\<\< FAILURE\!]?')

        for line in f.readlines():
            projectMatch = projectPattern.match(line)
            if projectMatch != None:
                # Append the previous project's results
                if len(projectResults) > 0 and projectResults["total"] != 0:
                    results[curProject] = projectResults
                    totals["total"] = totals["total"] + projectResults["total"]
                    totals["failures"] = totals["failures"] + projectResults["failures"]
                    totals["errors"] = totals["errors"] + projectResults["errors"]
                    totals["skipped"] = totals["skipped"] + projectResults["skipped"]
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
            totals["skipped"] = totals["skipped"] + projectResults["skipped"]
            totals["duration"] = totals["duration"] + projectResults["duration"]
        f.close()
        totals["results"] = results
        return totals

    def ResBuildCompare(self, leftName, left, rightName, right, only_diff = True):
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
        result=[]
        for filedir in [left, right]:
            with codecs.open(filedir+'/meta.arti', encoding='utf-8', mode='rb') as f:
                metadata = json.load(f)
                f.close
            buildsys = metadata.get('Primary Language','')
            result.append(self.resultParser(filedir+'/test_result.arti'))
        left_r = result[0]
        right_r = result[1]

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
    def PythonBuildSummary(self,file,parsekeys=["failed", "error", "skipped","passed"]):

        resultPattern = re.compile('^\=+([^\=]+)\=+$')
        keysPattern = []
        totals = {}
        for item in parsekeys :
            if item.strip() == '':
                continue
            totals[item] = 0
            regexstr = r'(\d*)\s(\b%s\b)'%(item)
            keysPattern.append(re.compile(regexstr))

        totals['duration'] = 0.0
        durPattern = re.compile(r'(\d*\.?\d*?)\sseconds')

        with codecs.open(file,encoding='utf-8',mode='rb')as f:

            for line in f.readlines():
                resultMatch = resultPattern.match(line)
                if resultMatch:
                    for p in keysPattern:
                        m = p.search(resultMatch.group(1))
                        if m:
                            totals[m.group(2)] = totals.get(m.group(2),0) + int(m.group(1))

                    d=durPattern.search(resultMatch.group(1))
                    if d:
                        totals['duration'] = float(d.group(1))
            f.close()

        res = {}
        res['total']    = totals['failed'] + totals['skipped'] + totals['passed']
        res['failures'] = totals['failed']
        res['errors']   = totals['error']
        res['skipped']  = totals['skipped']
        res['duration'] = totals['duration']
        res['results']  = {}
        return res

    def ResLogCompare(self, logName, leftName, left, rightName, right, only_diff = True):
        leftf = codecs.open(left+'/'+logName, encoding='utf-8', mode='rb')
        leftlog = leftf.readlines()
        leftf.close()

        rightf = codecs.open(right+'/'+logName, encoding='utf-8', mode='rb')
        rightlog = rightf.readlines()
        rightf.close()

        errorWords = logdiffutil.getErrorWords('./data/rules/errorwords')
        packageDict = logdiffutil.buildPackageDict('./data/rules/LinuxPackageList')

        lefttext = ""
        for line in leftlog:
            text = (line.replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;"))
            text = logdiffutil.renderline(text, errorWords, packageDict)
            lefttext = lefttext + text

        righttext = ""
        for line in rightlog:
            text = (line.replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;"))
            text = logdiffutil.renderline(text, errorWords, packageDict)
            righttext = righttext + text

        diff_obj = diff_match_patch.diff_match_patch()
        diffs = diff_obj.diff_main(lefttext, righttext)
        diff_obj.diff_cleanupSemantic(diffs)

        left_content = []
        right_content = []
        for (flag, data) in diffs:
            text = data.replace("\n", "<br>")

            if flag == diff_obj.DIFF_DELETE:
                # left_content.append("""<font style=\"background:#aaaaff;\">%s</font>""" % text)
                left_content.append("""%s""" % text)
            elif flag == diff_obj.DIFF_INSERT:
                #right_content.append("""<font style=\"background:#e6ffe6;\">%s</font>""" % text)
                right_content.append("""%s""" % text)
            elif flag == diff_obj.DIFF_EQUAL:
                left_content.append("%s" % text)
                right_content.append("%s" % text)

        leftres={}
        rightres={}
        leftres['diff'] = "".join(left_content)
        rightres['diff'] = "".join(right_content)

        res = {
                "diff": { leftName: leftres["diff"], rightName: rightres["diff"] },
                "results": {}
              }
        return res

    def JavaScriptBuildSummary(self, file, parsekeys=["failed", "error", "skipped", "passed"]):

        totals = {}
        for item in parsekeys:
            totals[item] = 0
        totals['duration'] = 0.0
        testframework = ''

        with codecs.open(file, encoding='utf-8', mode='rb')as f:
            readlines = f.readlines()
            f.close()

            for linenumber, line in enumerate(readlines):
                if testframework == '':
                    if linenumber < 10:
                        if line[0] == u'>':
                            for c in ['mocha', 'testem', 'jasmine', 'jest']:
                                if c in line:
                                    testframework = c
                                    break
                    else:
                        break
                else:
                    break
            readlines.reverse()

            if testframework == 'jasmine':  # 33 tests, 55 assertions, 0 failures
                totalPattern = re.compile(r'(\d+) tests, (\d+) assertions, (\d+) failures')
                for line in readlines:
                    match = totalPattern.match(line)
                    if match:
                        totals['passed'] = int(match.group(1) + match.group(2))
                        totals['failed'] = int(match.group(3))
                        break
            elif testframework == 'testem':
                failPattern = re.compile(r'# fail (\d+)')
                passPattern = re.compile(r'# pass (\d+)')
                for line in readlines:
                    match = failPattern.match(line)
                    if match:
                        totals['failed'] = int(match.group(1))
                        break
                    else:
                        match = passPattern.match(line)
                        if match:
                            totals['passed'] = int(match.group(1))
            elif testframework == 'jest':   # 1 test passed (1 total)
                                        # Run time: 0.855s
                passPattern = re.compile(r'(\d+) test passed \((\d+) total\)')
                durationPattern = re.compile(r'Run time: (\d+.?\d*)s')
                for line in readlines:
                    match = durationPattern.match(line)
                    if match:
                        totals['passed'] = match.group(1)
                        totals['failed'] = match.group(2) - match.group(1)
                        break
                    else:
                        match = passPattern.match(line)
                        if match:
                            totals['duration'] = float(match.group(1))
            else:                       # default  :  264 passing (18s)
                failPattern = re.compile(r'\s+(\d+)\).+')
                passPattern = re.compile(r'\s+(\d+) passing \((\d+[s|ms])\)')
                for line in readlines:
                    match = failPattern.match(line)
                    if match:
                        totals['failed'] = int(match.group(1))
                        break
                    else:
                        match = passPattern.match(line)
                        if match:
                            totals['passed'] = int(match.group(1))
                            durationstr = match.group(2)
                            if durationstr[-2:] == 'ms':
                                totals['duration'] = float(durationstr[:-2]) / 1000
                            else:
                                totals['duration'] = float(durationstr[:-1])

        res = {}
        res['total'] = totals['failed'] + totals['skipped'] + totals['passed']
        res['failures'] = totals['failed']
        res['errors']   = totals['error']
        res['skipped']  = totals['skipped']
        res['duration'] = totals['duration']
        res['results']  = {}
        return res

    def resultParser(self, logFile):
        """
        This method parses the log file which contains the result data, process the output summary and returns
        the results in JSON format
        Args:
            logFile(str): Absolute path with name of the log file to parse.
        Returns:
            JSON containing test result data.
        """
        totals = {
            "total": 0,
            "failures": 0,
            "errors": 0,
            "skipped": 0,
            "duration": 0,
            "results": {}
        }
        primaryLanguage = self.getPrimaryLanguageFromMeta(logFile)
        if primaryLanguage and primaryLanguage in ('Perl', 'C', 'C++'):
            return self.perlResultParser(logFile)
        elif primaryLanguage:
            resultPatterns = self.getResultPattern(primaryLanguage)
        else:
            return totals

        try:
            with open(logFile) as resultFile:
                resultFileData = resultFile.readlines()
                for line in resultFileData:
                    resultRegExList = resultPatterns.get('regex_list', None)
                    for regEx in resultRegExList:
                        resultMatch = regEx.match(line)
                        if type(resultMatch) == type(re.match("", "")):
                            # Control reaching here indicates primary language is one of the supported
                            # Also it means that the line in file we are looking at contains test result summary that we want

                            # Now split the summary lines based on delimiters to get the data required.
                            # Not using regular expression for fetching data, as using it will not allow a generalized method
                            # instead split string and fetch key value from it.
                            delimiterOne = resultPatterns.get('delimiterOne', ',')
                            delimiterTwo = resultPatterns.get('delimiterTwo', ' ')
                            infoFragments = line.split(delimiterOne)
                            totals = self.fillTotalArray(infoFragments, delimiterTwo, totals)
        except IOError as file_error:
            logger.warning("resultParser:: Error: File with name %s not found." % str(file_error))
        return totals

    def fillTotalArray(self, infoFragments, delimiter, totals):
        """
        This method updates the JSON test result data, based on data extracted from the test result log file.
        Args:
            infoFragments(list): Raw test summary key-value pair list.
            delimiter(str): used for separating key-value from infoFragments elements.
            totals(dict): final dictionary to be updated and returned.
        """

        keywordsToLookFor = ['test', 'tests', 'failed', 'passed', 'assertion', 'assertions', 'failures', 'errors', 'skips', 'skipped', 'total']
        def whichKeyword(value):
            """
            This method accepts a keyword and returns closest matching keyword which will be returned in final response
            Args:
                value(str): input string to check for
            Returns:
                translated keyword for response
            """
            if value in ['test', 'tests', 'total']:
                keywordToUse = 'total'
            elif value in ['failed', 'failures', 'failure']:
                keywordToUse = 'failures'
            elif value in ['skips', 'skipped']:
                keywordToUse = 'skipped'
            else:
                keywordToUse = value
            return keywordToUse

        def isStringInt(value):
            """
            This method checks if the given value is int or not and return True/False accordingly.
            Args:
                value(mixed): input string to check for
            Returns:
                Boolean indicating given value is integer or not.
            """
            try:
                int(value)
                return True
            except:
                return False

        def setKeyVal(keyValPair, totals):
            """
            This method finds the integer value and deduce its key, thereby updating the totals info with the key value.
            example:
                1) a string "[info] Passed: : Total 1" on splitting can contain following elements:
                ['[info]', 'Passed:', ':', 'Total', '1']

                2) a string "[info] Passed: : 1 Total" on splitting can contain following elements:
                ['[info]', 'Passed:', ':', '1', 'Total']

                So in order to figure out the correct key in generalized form, we need to check if there is another
                element after the numeric element or not.

                If numeric element is not the last element it means key is the last element, else key is the second last
                element.
            Args:
                keyValPair(list): List of all the words obtained from output summary string
                totals(dict): final dictionary to be updated and returned.
            Returns:
                dictionary with required test result data.
            """
            counter = 0
            for i in keyValPair:
                sanitizedValue = re.sub(r'([^\s\w]|_)+', '', i)
                if isStringInt(sanitizedValue):
                    if counter+1 > len(keyValPair):
                        sanitizedKey = re.sub(r'([^\s\w]|_)+', '', keyValPair[counter-1].lower())
                    else:
                        sanitizedKey = re.sub(r'([^\s\w]|_)+', '', keyValPair[counter+1].lower())
                    totals[whichKeyword(sanitizedKey)] = int(sanitizedValue)
                    return None
                counter = counter + 1
            return None

        for i in infoFragments:
            keyValPair = i.strip().split(delimiter)
            if len(keyValPair) == 2:
                if isStringInt(keyValPair[0]):
                    keyToUse = re.sub(r'([^\s\w]|_)+', '', keyValPair[1].strip())
                    # intentionally substituting any thing other than word, instead of replacing anything other than digit.
                    # reason being there can be some alphanumeric string which is not what is required.
                    ValueToUse = re.sub(r'([^\w]|)+', '', keyValPair[0])
                else:
                    keyToUse = re.sub(r'([^\s\w]|_)+', '', keyValPair[0].strip())
                    # intentionally substituting any thing other than word, instead of replacing anything other than digit.
                    # reason being there can be some alphanumeric string which is not what is required.
                    ValueToUse = re.sub(r'([^\w]|)+', '', keyValPair[1])
                keyword = filter(lambda x: x in keyToUse.lower(), keywordsToLookFor)
                if len(keyword):
                    totals[whichKeyword(keyword[0])] = int(ValueToUse)
            else:
                setKeyVal(keyValPair, totals)

        if int(totals['total']) == 0:
            totals['total'] = sum([val for val in totals.values() if isStringInt(val)])

        return totals

    def getPrimaryLanguageFromMeta(self, logFileName):
        """
        This method fetches primary language from the meta file based on given project test result file.
        Args:
            logFileName: Test result absolute path with file name.
        Returns:
            primary language based on meta file, if meta file not found it returns None
        """
        metaFileName = '%s/%s' % (logFileName[:logFileName.rfind('/')], 'meta.arti')
        try:
            with open(metaFileName) as metaFile:
                metaFileData = json.load(metaFile)
                return metaFileData.get("Primary Language", None)
        except AttributeError as metaDataError:
            logger.warning("getPrimaryLanguageFromMeta:: Error: File does not contain JSON Data, while reading fails with error: %s" % str(metaDataError))
        except IOError as fileNotAvailable:
            logger.warning("getPrimaryLanguageFromMeta:: Error: %s" , str(fileNotAvailable))

        return None

    def getResultPattern(self, primaryLanguage):
        """
        This method returns the set of regular expression for identifying the test result summary line from the
        result log.
        Args:
            primaryLanguage(str): language used for building and executing test for the package.
        Returns:
            A dict containing list of regular expression and the delimiters to use for fetching results.
        """
        # Following are some sample test log summaries for some supported languages.
        # Python:
        #    1 failed, 1 passed in 0.12 seconds
        #
        # Ruby:
        #    1 tests, 1 assertions, 0 failures, 0 errors, 0 skips
        #
        # PHP:
        #    Tests: 1, Assertions: 1, Failures: 1, Skipped: 1.
        #
        # Scala:
        #    [info] Passed: : Total 1, Failed 0, Errors 0, Passed 1, Skipped 0
        resultPattern = {
            'Python' : {
                'regex_list': [
                    re.compile(r'(.)*(\d+) (\w+), (\d+) (\w+)(\w*)(.*)')
                ],
                'delimiterOne': ',',
                'delimiterTwo': ' '
                },
            'Ruby' : {
                'regex_list': [
                   re.compile(r'(\d+) (\w+), (\d+) (\w+), (\d+) (\w+), (\d+) (\w+), (\d+) (\w*)')
                 ],
                'delimiterOne': ',',
                'delimiterTwo': ' '
            },
            'PHP': {
                'regex_list': [
                    re.compile(r'(\w*): (\d*), (\w+): (\d*), (\w+): (\d*), (\w+): (\d*)'),
                    re.compile(r'(\w*) \((\d+) (\w+), (\d+) (\w+)\)')
                 ],
                'delimiterOne': ',',
                'delimiterTwo': ':'
            },
            'Scala': {
                'regex_list': [
                     re.compile(r'(\[\w+\]) (\w+): : (\w+) (\d*), (\w+) (\d*), (\w+) (\d*), (\w+) (\d*), (\w+) (\d*)')
                 ],
                'delimiterOne': ',',
                'delimiterTwo': ':'
            },
            'JavaScript': {
                'regex_list': [
                    re.compile(r'(\d+) tests, (\d+) assertions, (\d+) failures'),
                    re.compile(r'# fail (\d+)'),
                    re.compile(r'(\d+) test passed \((\d+) total\)'),
                    re.compile(r'\s+(\d+)\).+'),
                    re.compile(r'\s+(\d+) passing \((\d+[s|ms])\)')
                ],
                'delimiterOne': ',',
                'delimiterTwo': ' '
            },
            'Java': {
                'regex_list': [
                    re.compile(r'Tests run: (\d*), Failures: (\d*), Errors: (\d*), Skipped: (\d*), Time elapsed: (\d*\.?\d*) sec[ \<\<\< FAILURE\!]?')
                 ],
                'delimiterOne': ',',
                'delimiterTwo': ':'
            }
        }

        return resultPattern.get(primaryLanguage, None)

    def perlResultParser(self, logFile):
        # Read line by line and search for pattern like "*.... ok"
        # If ".... skipped" then add to skipped.
        # If ".... error" then add to error.
        # If ".... fail" then add to failure.
        totals = {
            "total": 0,
            "failures": 0,
            "errors": 0,
            "skipped": 0,
            "duration": 0,
            "results": {}
        }

        try:
            testLogFile = open(logFile)
            logFileData = testLogFile.readlines()
            for line in logFileData:
                dataKey = None
                if '.... fail' in line:
                    dataKey = 'failures'
                elif '.... error' in line:
                    dataKey = 'error'
                elif '.... skip' in line:
                    dataKey = 'skipped'
                elif 'Tests=' in line:
                    try:
                        totalStr = line[line.find('Tests='):].split(',')[0]
                        totals['total'] = int(totalStr[totalStr.find('=')+1:])
                    except Exception as e:
                        logger.warning("perlResultParser:: Error: %s" , str(e))
                    continue
                else:
                    continue

                if dataKey:
                    totals[dataKey] += 1
        except Exception as e:
            logger.warning("perlResultParser:: Error: %s" , str(e))
        finally:
            testLogFile.close()
        return totals
