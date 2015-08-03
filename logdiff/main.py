from flask import Flask, render_template, request, json
from werkzeug.utils import secure_filename
import diff_match_patch
import re
import os, codecs
import sys

sys.path.append("..")
import logdiffutil

app = Flask(__name__)

# This is the path to the upload directory
UPLOAD_FOLDER = 'compfiles'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'log', 'cfg','arti'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route("/")
def main():
    return render_template("main.html")

# Get diff log output
@app.route("/getFileDiffResults", methods = ['POST'])
def getFileDiffResults():
    try:
        file1 = request.files['file1']
        file2 = request.files['file2']
    except KeyError:
        return json.jsonify(status="failure",
                    error="No File selected for upload"), 400

    path1 = os.path.dirname(os.path.abspath(__file__)) + "/uploads/file1"
    if not os.path.exists(path1):
        os.makedirs(path1)
    if file1 and allowed_file(file1.filename):
        fname1 = secure_filename(file1.filename)
        file1.save(os.path.join(path1, fname1))
    else:
        return json.jsonify(status="failure",
                error="Allowed file extensions are.txt, .log, .cfg, .arti"), 400

    path2 = os.path.dirname(os.path.abspath(__file__)) + "/uploads/file2"
    if not os.path.exists(path2):
        os.makedirs(path2)
    if file2 and allowed_file(file2.filename):
        fname2 = secure_filename(file2.filename)
        file2.save(os.path.join(path2, fname2))
    else:
        return json.jsonify(status="failure",
                error="Allowed file extensions are.txt, .log, .cfg, .arti"), 400


    leftf = codecs.open(path1+'/'+fname1,encoding='utf-8',mode='rb')
    leftlog = leftf.readlines()
    leftf.close()

    rightf = codecs.open(path2+'/'+fname2,encoding='utf-8',mode='rb')
    rightlog = rightf.readlines()
    rightf.close()

    errorWords = logdiffutil.getErrorWords('../data/rules/errorwords')
    packageDict = logdiffutil.buildPackageDict('../data/rules/LinuxPackageList')

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
            left_content.append("""<font style=\"background:#ceceff;\">%s</font>""" % text)
            #left_content.append("""%s""" % text)
        elif flag == diff_obj.DIFF_INSERT:
            right_content.append("""<font style=\"background:#e6ffe6;\">%s</font>""" % text)
            #right_content.append("""%s""" % text)
        elif flag == diff_obj.DIFF_EQUAL:
            left_content.append("%s" % text)
            right_content.append("%s" % text)

    return json.jsonify(status = "ok",
                leftname = fname1,
                rightname = fname2,
                leftcontent = "".join(left_content),
                rightcontent = "".join(right_content))

@app.route('/getTextDiffResults', methods=['POST'])
def getTextDiffResults():
    leftlog = request.form['text1']
    rightlog = request.form['text2']

    errorWords = logdiffutil.getErrorWords('../data/rules/errorwords')
    packageDict = logdiffutil.buildPackageDict('../data/rules/LinuxPackageList')

    lefttext = ""
    leftlines = re.split(r"(\r|\n)+",leftlog)
    for line in leftlines:
        text = (line.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;"))
        text = logdiffutil.renderline(text, errorWords, packageDict)
        lefttext = lefttext + text

    righttext = ""
    rightlines = re.split(r"(\r|\n)+",rightlog)
    for line in rightlines:
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
            left_content.append("""<span><font style=\"background:#ceceff;\">%s</font><span>""" % text)
            # left_content.append("""%s""" % text)
        elif flag == diff_obj.DIFF_INSERT:
            right_content.append("""<span><font style=\"background:#e6ffe6;\">%s</font><span>""" % text)
            #right_content.append("""%s""" % text)
        elif flag == diff_obj.DIFF_EQUAL:
            left_content.append("<span>%s</span>" % text)
            right_content.append("<span>%s</span>" % text)

    return json.jsonify(status = "ok",
                    leftname = "text fragment1",
                    rightname = "text fragment2",
                    leftcontent = "".join(left_content),
                    rightcontent = "".join(right_content))

# Get diff log output
@app.route("/logdiff", methods = ['GET'])
def getlogdiff():
    file1=request.args.get('file1','')
    file2=request.args.get('file2','')

    if len(file1) == 0 or not allowed_file(file1) or len(file2) == 0 or not allowed_file(file2):
        return render_template('fileerror.html')

    leftf = codecs.open(file1,encoding='utf-8',mode='rb')
    leftlog = leftf.readlines()
    leftf.close()

    rightf = codecs.open(file2,encoding='utf-8',mode='rb')
    rightlog = rightf.readlines()
    rightf.close()

    errorWords = logdiffutil.getErrorWords('../data/rules/errorwords')
    packageDict = logdiffutil.buildPackageDict('../data/rules/LinuxPackageList')

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
            left_content.append("""<font style=\"background:#ceceff;\">%s</font>""" % text)
            #left_content.append("""%s""" % text)
        elif flag == diff_obj.DIFF_INSERT:
            right_content.append("""<font style=\"background:#e6ffe6;\">%s</font>""" % text)
            #right_content.append("""%s""" % text)
        elif flag == diff_obj.DIFF_EQUAL:
            left_content.append("%s" % text)
            right_content.append("%s" % text)

    return render_template('output.html', leftname=file1, rightname=file2, left_content="".join(left_content), right_content="".join(right_content))
    #return render_template('output.html', left_content="Hello", right_content="world")




if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int("5555")
    )