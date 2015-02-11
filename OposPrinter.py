#!/usr/bin/python
# -*- coding: utf-8 -*-

from usb import core
import types
from PIL import Image


class OposPrinter:
    def __init__(self, idVendor = None, idProduct = None):
        self.devices = []
        if(idVendor is not None) and (idProduct is not None):
            self.devices = list(core.find(find_all=True,
                                         idVendor=idVendor, idProduct=idProduct))
        else:
            if(idVendor is not None):
                self.devices = list(core.find(find_all=True, idVendor=idVendor))
            else:
                if(idProduct is not None):
                    self.device = list(core.find(find_all=True,
                                                 idProduct=idProduct))
                else:
                    self.devices = list(core.find(find_all=True))

    def ChangeDevice(self, **idDevice):
        devs = []
        for dev in self.devices:
            for key in idDevice:
                if(getattr(dev, key) == idDevice[key]):
                    devs += dev
        self.devices = devs

    def Claim(self, timeout):
        for dev in self.devices:
            confs = dev.configurations()
            for conf in confs:
                interfaces = conf.interfaces()
                for interface in interfaces:
                    #print interface
                    if(dev.is_kernel_driver_active(interface.bInterfaceNumber)):
                        dev.detach_kernel_driver(interface.bInterfaceNumber)
            dev.set_configuration()
            
    def InitDevice(self):
        for dev in self.devices:
            dev.write(2, chr(0x1B) + chr(40))

    def Interfaces(self):
        for dev in self.devices:
            confs = dev.configurations()
            for conf in confs:
                print conf
                interfaces = conf.interfaces()
                for interface in interfaces:
                    print interface
                return interfaces
        
    def PrinterState(self):
        '''
        If return ('B', 255), then printer not found. Please re initialized class
        and make sure that the settings are correct
        '''
        State = ('B', 255)
        for dev in self.devices:
            dev.write(2, chr(0x10) + chr(0x4) + chr(3))
            State = dev.read(0x81, 1)
        return State
        
    def PrintLine(self, Position=0, Line='', decode='utf-8', encode = 'cp866'):
        for dev in self.devices:
            dev.write(2, chr(0x1B) + chr(0x61) + chr(0))
            dev.write(2, Line.decode(decode).encode(encode))
            dev.write(2, chr(0x1B) + chr(0x61) + chr(0))
        return
    
    def PrintBarcode(self, Position=0, Line='', positionHRI = 2,
                     height = 130, width = 2, TypeBarcode = 72):
        for dev in self.devices:
            dev.write(2, chr(0x1B) + chr(0x61) + chr(1))
            dev.write(2, chr(0x1d) + chr(0x48) + chr(positionHRI))
            dev.write(2, chr(0x1d) + chr(0x68) + chr(height))
            dev.write(2, chr(0x1d) + chr(0x77) + chr(width))
            dev.write(2, chr(0x1d) + chr(0x6b) + chr(TypeBarcode) +
                      chr(len(Line)) +
                          Line)
            dev.write(2, chr(0x1B) + chr(0x61) + chr(0))
        return

    def GetBitmapData(self, imageName = ''):
        img = Image.open(imageName)
        thr = 127
        index = 0
        multiplier = 576
        scale = multiplier/img.size[0]
        xheight = img.size[0] * scale
        xwidth = img.size[1] * scale
        dimension = xheight * xwidth
        dots = []
        for y in xrange(xwidth):
            for x in xrange(xheight):
                _x = x/scale
                _y = y/scale
                color = img.getpixel((_x,_y))
                dots.append((color < thr))
        return {'Dots' : dots, "Height":xheight, "Width":xwidth}
    
    def PrintImage(self, Position=0, FileName='enter.bmp'):
        '''    
        data = self.GetBitmapData(FileName)
        self.d = data
        n1 = data['Width'] % 256
        n2 = data['Width'] / 256
        offset = 0
        for dev in self.devices:
            dev.write(2, chr(0x1b)+chr(0x33)+chr(24))
            while offset < data['Height']:
                dev.write(2, chr(0x1b)+chr(0x2a)+chr(33) + chr(n1) + chr(n2))
                for x in xrange(data['Width']):
                    for k in xrange(3):
                        slices = 0
                        for b in xrange(8):
                            y = (((offset/8) +k) * 8) + b
                            i = (y * data['Width']) + x
                            v = 0
                            if(i<len(data['Dots'])):
                                v = data['Dots'][i]
                            if v == True:
                                slices += 1
                            else:
                                slices = slices << 1
                        dev.write(2, chr(slices))
                    offset += 24
                    dev.write(2, chr(0x0A))
            '''
        for dev in self.devices:
        #    dev = self.devices[0]
            img = Image.open(FileName)
            n1 = img.size[0] % 256
            n2 = img.size[0] / 256
        #    self.img = img
            dev.write(2, chr(0x1b) + '3' + chr(23))
            for y in xrange(0, img.size[1], 24):
                dev.write(2, chr(0x1b)+chr(0x2a)+chr(33) + chr(n1) + chr(n2))
                for x in xrange(img.size[0]):
                    byte = 0
                    for k in xrange(3):
                        byte = 0
                        for i in xrange(8):
                            if y+i+8*k > img.size[1]-1:
                                pixel = 0
                            else:
                                try:
                                    pixel = img.getpixel((x,y+i+8*k))
                                except:
                                    print 'error (x=%i,y=%i) ' % (x,y+i+8*k)
                            if pixel<127:
                                byte = byte << 1
                                byte += 1
                            else:
                                byte = byte << 1
                        #print byte
                        dev.write(2, chr(byte))
                dev.write(2, chr(0x0a))
        return
    
    def Cut(self, Indent = 10):
        for dev in self.devices:
            dev.write(2, chr(0x1d)+chr(0x56)+chr(65)+chr(Indent))
        return
    
    def SelectCodepage(self, codepage = 7):
        for dev in self.devices:
            dev.write(2, chr(0x1b)+chr(0x74)+chr(codepage))

   

device = OposPrinter(idVendor = 0x1d90)
device.Claim(0)
device.InitDevice()
device.SelectCodepage()
device.PrintLine(0, 'Вот текст вот и печатаем\n')
device.PrintLine(0, 'Вот текст вот и печатаем\n')
device.PrintBarcode(0, '123')
device.PrintBarcode(0, 'COXD-202345')
device.PrintImage()
device.PrintLine(0, 'Вот текст вот и печатаем\n')
device.Cut()
