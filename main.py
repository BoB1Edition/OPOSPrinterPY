#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, request, Response
import sys
import usb
from OposPrinter import *
import re
import platform
import getopt
import os
import json

app = Flask(__name__)
global device
global conf


dict_tag = {
    "[b]":chr(0x1b)+chr(0x45)+chr(0x1),
    "[/b]":chr(0x1b)+chr(0x45)+chr(0x0),
    "[left]":chr(0x1B) + chr(0x61) + chr(0),
    "[center]":chr(0x1B) + chr(0x61) + chr(1),
    "[right]":chr(0x1B) + chr(0x61) + chr(2),
    }

def main():
    global conf 
    conf = {}
    if os.access('OposServer.json',os.R_OK):
        fp = file('OposServer.json', 'r')
        conf = json.load(fp)
    else:
        conf = {
            'port':8088,
            'codepage':'utf8',
            'device': {
                'idVendor':0x0dd4,
            }
        }
        fp = file('OposServer.json', 'w')
        json.dump(conf, fp)
        fp.close()
        main()
    global device
    device = OposPrinter(conf['device']['idVendor'])
    device.Claim(0)
    app.add_url_rule('/', view_func=default, methods=['POST','GET'])
    app.add_url_rule('/print', view_func=_print, methods=['POST'])
    app.add_url_rule('/status', view_func=_status, methods=['GET'])
    app.run(port=conf['port'], debug=True, host='0.0.0.0')

def default():
    global device
    if request.method == 'GET':
        return _status()
    if request.method == 'POST':
        return _print()
def _status():
    global device
    device.InitDevice()
    printstate = device.PrinterState()
    print printstate[0]
    #print printstate[1]
    if(printstate[0] == 18):
        answer = '{\"code\": 0, \"message\": \"Готов к работе\"}'
    else:
        answer = '{\"code\": 1,\"message\": \"Не Готов к работе\"}'
    return Response(response = answer,
                    status=200,
                    mimetype="application/json; charset=\"utf-8\"")

def _print():
    global conf
    global device
    img_tag = re.compile("\[img\](.+)\[/img\]")
    bc_tag = re.compile("\[bc\](.+)\[/bc\]")
    tag = re.compile("\[.+?\]")
    device.InitDevice()
    device.SelectCodepage()
    for line in request.data.split('\n'):
        img = img_tag.match(line)
        if img:
            print img.group(1)
            device.PrintImage(0, img.group(1))
            continue
        bc = bc_tag.match(line)
        if bc:
            device.PrintBarcode(1, bc.group(1))
            continue
        if(tag.search(line)):
            for k, v in dict_tag.iteritems():
                line = line.replace(k, v)
        device.PrintLine(Line = line)
    print 'Cut'
    device.Cut()           
    return Response(status = 200, response = request.data)

main()
