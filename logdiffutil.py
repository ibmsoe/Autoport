
def renderline(text, errorWords, packageDict):
    if 'failures: 0' in text.lower() or 'errors: 0' in text.lower():
        return text

    for errword in errorWords:
        if errword in text.lower():
            words = text.lower().strip().split(' ')
            for word in words:
                if packageDict.has_key(word):
                    text = (text.replace(word,"""<font style=\"background:#f9f900;\">%s</font>"""%(word)))
            return ("""<span><font style=\"background:#ff9797;\">%s</font></span>""" % text)
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
