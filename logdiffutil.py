
def renderline(text, errorWords, packageDict, diffPart):
    if 'failures: 0' in text.lower() or 'errors: 0' in text.lower():
        return text

    # Check if it is a compiling command
    compilers = ['gcc', 'g++', 'clang', 'clang++', 'clips', 'erlang', 'javac', 'luac', 'scala']
    noEndsWithStr = '[~!@#$%^&*()_{}":;\']+$'
    firstword = text.strip().split(' ', 1)[0]
    lastChar = ""
    if len(firstword)!=0:
        lastChar = firstword[len(firstword) - 1]
    for compiler in compilers:
        if firstword.startswith(compiler) and not lastChar in noEndsWithStr:
            return text

    # Check if it contains error words
    for errword in errorWords:
        if errword in text.lower():
            words = text.strip().split()
            for word in words:
                if packageDict.has_key(word.lower()):
                    text = (text.replace(word,"""<font ondblclick=\"onClickErrorText(%s)\" style=\"background:#f9f900;\">%s</font>"""%(word,word)))
            return ("""<font ondblclick=\"onClickErrorText('%s','%s')\" style=\"background:#ff9797;\">%s</font>""" % (text,diffPart,text))
    return text

def getErrorWords(filename):
    errorWords = []
    with open(filename, 'r') as f:
        for line in f.readlines():
            errorWords.append(line.strip('\n'))
        f.close()
    return errorWords

def buildPackageDict(filename):
    dict = {}
    with open(filename,'r') as f:
        for line in f.readlines():
            index = line.find(', ', 0)
            packageName = line[:index]
            packageDesc = line[index+2:]
            if ' ' in packageName:
                packageName = packageName[:packageName.find(' ', 0)]
            dict[packageName] = packageDesc
        f.close()
    return dict
