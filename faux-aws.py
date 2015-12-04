import os
import pprint
from flask import Flask, request, render_template_string
from werkzeug.serving import run_simple

aws_endpoints = Flask(__name__ + "aws")
aws_endpoints.debug = True

imdsNotFoundXml = """<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
 <head>
  <title>404 - Not Found</title>
 </head>
 <body>
  <h1>404 - Not Found</h1>
 </body>
</html>
"""

awsServiceList = [ 'ec2' ]

@aws_endpoints.route('/', defaults={'path': ''})
@aws_endpoints.route('/<path:path>', methods=['GET','POST'])
def imds(path):
    root = "./data"

    if path.split('/', 1)[0] in awsServiceList:
        path = os.path.join(path.split('/', 1)[0], request.form['Action'] if 'Action' in request.form else '')
    else:
        path = os.path.join('imds', path)
    internal_path = os.path.join(root, path)
    print 'internal_path = "' + internal_path + '"'
    print 'remote address = "' + request.environ['REMOTE_ADDR'] + '"'
    if os.path.exists(internal_path):
        if (os.path.isdir(internal_path)) and path.endswith('/'):
            return '\n'.join(os.listdir(internal_path))
        elif (os.path.isfile(internal_path)) and not path.endswith('/'):
            internal_file = open(internal_path, 'r')
            contents = internal_file.read()
            internal_file.close()
            return render_template_string(contents, remote_address=request.environ['REMOTE_ADDR'])
    return imdsNotFoundXml


if __name__ == "__main__":
    run_simple('0.0.0.0', 5000, aws_endpoints, use_debugger=True, use_reloader=True)
