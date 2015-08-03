import os
import webbrowser
import urllib
import httplib
import sys
import subprocess
import time

def usage():
    print 'Two usages:'
    print '\t(1) python logdiff.py file1 file2'
    print '\t(2) python logdiff.py and access the app by your bowser. '

if __name__=="__main__":
    if len(sys.argv) > 1:
        if len(sys.argv) == 3:
            subprocess.Popen(["python", "main.py"])
            time.sleep(3)
            file1 = sys.argv[1]
            file2 = sys.argv[2]
            file1 = os.path.abspath(file1)
            file2 = os.path.abspath(file2)
            file1 = file1.replace("\\","\\\\")
            file2 = file2.replace("\\","\\\\")
            url = r'http://127.0.0.1:5555/logdiff?file1='+file1+'&file2='+file2
            print url
            webbrowser.open(url)
        else:
            usage()
            sys.exit()
    else:
        subprocess.Popen(["python", "main.py"])
        time.sleep(3)
        webbrowser.open("http://127.0.0.1:5555")