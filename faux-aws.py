import os
import re
import lxml.etree as etree
import services.ec2
from common.filter import Filter, getFilters
from flask import Flask, request, render_template_string
from werkzeug.serving import run_simple

aws_endpoints = Flask(__name__ + "aws")
aws_endpoints.debug = True

awsServices = {
    'ec2': services.ec2
}

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
      
def readDataFile(filename):
    data_file = open(filename, 'r')
    contents = data_file.read()
    data_file.close()
    return contents

@aws_endpoints.route('/', defaults={'path': ''})
@aws_endpoints.route('/<path:path>', methods=['GET','POST'])
def handler(path):
    root = "./data"

    service = path.split('/', 1)[0]
    if service in awsServices:
        action = request.form['Action'] if 'Action' in request.form else ''
        path = os.path.join(path.split('/', 1)[0], action)
        data_path = os.path.join(root, path)
        if os.path.isfile(data_path):
            contents = readDataFile(data_path)
            root = etree.fromstring(contents)
            filters = getFilters(request.form)
            if hasattr(awsServices[service], 'filter'):
                awsServices[service].filter(action, root, filters)
            return render_template_string(etree.tostring(root), remote_address=request.environ['REMOTE_ADDR'])
        return ""
    else:
        path = os.path.join('imds', path)
        data_path = os.path.join(root, path)
        if (os.path.isdir(data_path)) and path.endswith('/'):
            return '\n'.join(os.listdir(data_path))
        elif os.path.isfile(data_path):
            contents = readDataFile(data_path)
            return render_template_string(contents, remote_address=request.environ['REMOTE_ADDR'])
        return imdsNotFoundXml


if __name__ == "__main__":
    run_simple('0.0.0.0', 5001, aws_endpoints, use_debugger=True, use_reloader=True)
