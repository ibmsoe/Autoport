The program is coded under python 2.7.9, flask-0.10.1, diff-match-path 20121119.

Current Capabilities
========
 - Compare two file logs or two text fragments
 - Highlight the differences between the two pieces of text in light green
 - Highlight the error lines if there is an error word appears in light red. The error words are predefined in ./data/rules. You can define yours.
 - Highlight the package name in light yellow if there is a package appeared in the same line with the errors .


Packaging and Delivery
(Note that this section is not for the end user.)
========
Since logdiff standalone tool is a sub-project of Autoport, you need to clone the repository of Autoport and package the source code manually.
    git clone ssh://soe-gerrit/autoport && scp -p soe-gerrit:hooks/commit-msg autoport/.git/hooks/
    cd autoport
    tar czvf logdiff.tgz data/ logdiff/ logdiffutil.py

Dependencies
========
Install [pip](https://pip.pypa.io/en/latest/installing.html) and then run these commands to install dependencies:

    pip install Flask
    pip install diff_match_patch

Running
========
After installing dependencies,
(1) copy and unzip the tgz file:
    mkdir your-work-dir
    copy logdiff.tgz to your-work-dir
    cd your-work-dir
    tar xzvf logdiff.tgz
(2) change the current directory
    cd logdiff
(3) run the app.
    There are two methods for the app running

    (3.1) web service
            python main.py
            Open your browser manually
            Navigate to http://127.0.0.1:5555/ to access the app

    (3.2) command line
            python logdiff.py /path-to/file1 /path-to/file2
            (e.g. python logdiff.py C:\1.txt C:\2.txt)
            After your browser opens, you can change the url parameters directly for other files comparison.Please note the format of the parameters.
            (e.g. http://127.0.0.1:5555/logdiff?file1=c:\\1.txt&file2=c:\\2.txt)

            or

            python logdiff
            Your browser will be launched automatically. After your browser opens, you can specify the filename in the html form.

Next Steps
=========
- Provide error diagnosis by integrating Google Search API



