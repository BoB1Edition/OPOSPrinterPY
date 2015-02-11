from PIL import Image
import random
import struct

def RandomName():
    random.seed()
    sizename = random.randint(4, 25)
    name = ''
    for lengh in xrange(sizename):
        a = random.randint(0, 3)
        if a == 0:
            name += chr(random.randint(0x30, 0x39))
        if a == 1:
            name += chr(random.randint(0x41, 0x5A))
        if a == 2:
            name += chr(random.randint(0x61, 0x7a))
        if a == 3:
            name += chr(0x5f)
    return name

random.seed()
img = Image.open('enter.bmp')



f1 = file(RandomName()+'.bin', 'w')
#f2 = file(RandomName()+'.bin', 'wb')

for x in xrange(img.size[1]):
    value = 0;
    for y in xrange(img.size[0]):
        pixel = img.getpixel((y, x))
        if pixel < 127:
            f1.write("1")
        else:
            f1.write("0")
    f1.write('%s\n' % value)
#    f2.write(struct.pack('h', value))
            


    
