#!/usr/bin/python
# -*- coding: utf-8 -*-

from usb import core
import types
from PIL import Image
import os

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
                    if(dev.is_kernel_driver_active(interface.bInterfaceNumber)):
                        dev.detach_kernel_driver(interface.bInterfaceNumber)
            dev.set_configuration()
            
    def InitDevice(self):
        for dev in self.devices:
            dev.write(2, chr(0x1B) + chr(0x40))
            dev.write(2, chr(0x1b)+chr(0x45)+chr(0x0))
            dev.write(2, chr(0x1b)+chr(0x2d)+chr(0x0))

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
            dev.write(2, chr(0x1B) + chr(0x61) + chr(Position))
            dev.write(2, chr(0x1b)+chr(0x45)+chr(0x0))
            dev.write(2, Line.decode(decode).encode(encode))
            dev.write(2, chr(0x1B) + chr(0x61) + chr(0))
            dev.write(2, chr(0x1b)+chr(0x45)+chr(0x0))
            dev.write(2, chr(0x0a))
        return
    
    def PrintBarcode(self, Position=1, Line='', positionHRI = 2,
                     height = 130, width = 2, TypeBarcode = 4):
        #Line = '{A'+'{1'+'{2'+'{3'+'{4'+Line
        #Line = Line.replace('O', 'O')
        for dev in self.devices:
            dev.write(2, chr(0x1B) + chr(0x61) + chr(Position))
            dev.write(2, chr(0x1d) + chr(0x66) + chr(0))
            dev.write(2, chr(0x1d) + chr(0x48) + chr(positionHRI))
            dev.write(2, chr(0x1d) + chr(0x68) + chr(height))
            dev.write(2, chr(0x1d) + chr(0x77) + chr(width))
            dev.write(2, chr(0x1d) + chr(0x6b) + chr(TypeBarcode) +
                      #chr(len(Line)) +
                          Line+chr(0))
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

    def PrintImage2(self, Position=0, FileName='enter.bmp'):
        FileName = FileName.replace('\\', os.sep)
        for dev in self.devices:
            img = img = Image.open(FileName)
            img = img.convert('1')
            n1 = 8
            n2 = 8
            dev.write(2, chr(0x1B) + chr(0x61) + chr(Position))
            dev.write(2, chr(0x1d) + chr(0x2a) + chr(n1) + chr(n2))
            byte = 0b10000000
            for j in xrange(8*8):
                for i in xrange(8):
                    dev.write(2, chr(byte))
                    if byte == 0:
                        byte = 0b10000000
                        continue
                    byte = byte >> 1
            #dev.write(2, n1*n2*8)
            dev.write(2, chr(0x1d) + chr(0x2f) + chr(1))

        """
            n1 = 33
            n2 = 23
            dev.write(2, chr(0x1B) + chr(0x61) + chr(Position))
            dev.write(2, chr(0x1d) + chr(0x2a) + chr(n1) + chr(n2))
            for x in xrange(n1*8):
                #print 'x= %i' % (x)
                for _n2 in xrange(n2):
                    #print '_n2= %i' % (_n2)
                    byte = 0
                    for i in xrange(8):
                        y = _n2*8+i
                        #print 'y= %i' % (y)
                        try:
                            if (y > img.size[1]-1) or (x>img.size[0]-1):
                                pixel = 255
                            else:
                                pixel = img.getpixel((x,y))
                        except:
                            print 'error (x=%i,y=%i) ' % (x,_y)
                            pixel = 255
                        if pixel<127:
                            byte = byte << 1
                            byte += 1
                        else:
                            byte = byte << 1
                    dev.write(2, chr(byte))
            dev.write(2, chr(0x2d)+chr(0x2f)+chr(3))
            """
    
    def PrintImage(self, Position=1, FileName='enter.bmp'):
        FileName = FileName.replace('\\', os.sep)
        for dev in self.devices:
            img = Image.open(FileName)
            img = img.convert('1')
            n1 = img.size[0] % 256
            n2 = img.size[0] / 256
            dev.write(2, chr(0x1B) + chr(0x61) + chr(Position))
            dev.write(2, chr(0x1b) + '3' + chr(40))
            dev.write(2, chr(0xa)+chr(13))
            dev.write(2, chr(0x1b) + '0')
            for y in xrange(0, img.size[1], 24):
                dev.write(2, chr(0x1b)+chr(0x2a)+chr(33) + chr(n1) + chr(n2))
                for x in xrange(img.size[0]):
                    byte = 0
                    for k in xrange(3):
                        byte = 0
                        for i in xrange(8):
                            _y = y+i+8*k
                            if _y > img.size[1] - 1:
                                pixel = 255
                            else:
                                try:
                                    pixel = img.getpixel((x,_y))
                                except:
                                    print 'error (x=%i,y=%i) ' % (x,_y)
                                    pixel = 255
                            if pixel<127:
                                byte = byte << 1
                                byte += 1
                            else:
                                byte = byte << 1
                        #f.write(chr(byte))
                        dev.write(2, chr(byte))
                #f.write(chr(0x0a))
                dev.write(2, chr(0xa)+chr(13))
        #f.write(chr(0x1B) + chr(0x61) + chr(0))
        dev.write(2, chr(0x1B) + chr(0x61) + chr(0))
        #f.close()    
        return
    
    def Cut(self, Indent = 10):
        for dev in self.devices:
            #dev.write(2, chr(0x1D) + chr(0x65) + chr(0x1) )
            dev.write(2, chr(0x1d)+chr(0x56)+chr(65)+chr(Indent))
            dev.write(2, chr(0x0c))
        return
    
    def SelectCodepage(self, codepage = 7):
        for dev in self.devices:
            dev.write(2, chr(0x1b)+chr(0x74)+chr(codepage))


device = OposPrinter(idVendor = 0x0dd4)
device.Claim(0)
device.InitDevice()
device.PrintImage2(FileName = 'icons/enter.bmp')
device.Cut()
