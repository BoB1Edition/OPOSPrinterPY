#!/usr/bin/python

from flask import Flask, request, Response
import sys
import usb
from OposPrinter import *
import re


app = Flask(__name__)
global device

dict_tag = {
    "[b]":"<b>",
    "[/b]":"</b>",
    "[center]":"<center>",
    "[right]":"<right>",
    }

def main():
    global device
    device = OposPrinter(idVendor = 0x1d90)
    app.add_url_rule('/', view_func=default, methods=['POST','GET'])
    app.add_url_rule('/print', view_func=_print, methods=['POST'])
    app.add_url_rule('/status', view_func=_status, methods=['GET'])
    app.run(port=8088, debug=True)

def default():
    if request.method == 'GET':
        return _status()
    if request.method == 'POST':
        return _print()
def _status():
    global device
    return Response(response = device.PrinterState(),#OPOSStatus(),
                    status=200,
                    mimetype="application/json")
def _print():
    global device
    #device = OposPrinter(idVendor = 0x1d90)
    img_tag = re.compile("\[img\](.+)\[/img\]")
    bc_tag = re.compile("\[bc\](.+)\[/bc\]")
    tag = re.compile("\[.+?\]")
    device.Claim(0)
    device.SelectCodepage()
    for line in request.data.split('\n'):
        img = img_tag.match(line)
        if img:
            device.PrintImage(img.group(1))
            continue
        bc = bc_tag.match(line)
        if bc:
            device.PrintBarcode(bc.group(1))
            continue
        if(tag.search(line)):
            for k, v in dict_tag.iteritems():
                line = line.replace(k, v)
        device.PrintLine(Line = line)        
    return Response(status = 200, response = request.data)
    
main()
