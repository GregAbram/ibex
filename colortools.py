import os, pdb
import numpy as np
from PIL import Image
from glob import glob
from time import sleep
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
import xml.etree.ElementTree as ET
import cv2
import json

with open('%s/gamma.csv' % __file__.rsplit('/',1)[0]) as f:
    s = f.read()
    
gammaTable = np.array([float(i) for i in s.split(',')])/255.0

def GammaCorrect(img):
    return gammaTable[np.around(img*4095.0).astype('i2')]

ramp = np.arange(256)/255.0
gscale = np.column_stack((ramp, ramp, ramp))

def LinearMap():
    return ramp

def SolidGray(g):
    a = np.ones(256)*g
    return np.column_stack((a, a, a))

def GrayScale(img):
    return gscale[np.around(img*255.0).astype('i2')]
    
def SRGB(img):
    return np.around(img*255.0).astype('u1')

def reverse_colormap(cmap):
    return np.flip(cmap, axis=0)

def load_colormap_csv(name):
    f = open(name)
    colormap = []
    for line in f:
        try:
            row = [float(i) for i in line.strip().split(',')]
            colormap.append(row)
        except:
            continue
    while len(colormap) < 256:
        colormap.append(colormap[-1])

    cmap = [colormap[i] for i in range(256)]
    return (np.vstack(cmap)).astype('f4')

def load_colormap_json(fname):
    with open(fname) as f:
        j = json.load(f)

        if isinstance(j, dict):
          j = j['colormaps']

        if isinstance(j, list):
            j = j[0]

        if 'points' in j:
          icmap = np.vstack([[i['x'], i['r'], i['g'], i['b']] for i in j['points']])
        elif 'RGBPoints' in j:
          icmap = np.array(j['RGBPoints']).reshape(-1,4)
        else:
          print(fname, "not a colormap?")
          return None

        icmap = icmap[icmap[:,0].argsort()]
        i0 = 0
        i1 = 1
        xmin = icmap[0][0]
        xmax = icmap[-1][0]
        cmap = []
        for i in range(256):  
            x = xmin + (i / (255.0))*(xmax - xmin)
            if (x > xmax): 
                x = xmax;
            while icmap[i1][0] < x:
                i0 = i0 + 1
                i1 = i1 + 1
            d = (x - icmap[i0][0]) / (icmap[i1][0] - icmap[i0][0])
            cmap.append(icmap[i0] + d*(icmap[i1] - icmap[i0]))
            
        cmap = np.vstack(cmap)
        cmap = cmap[:,1:]
        return cmap.astype('f4')
        
    
def load_opacitymap_json(fname):
    with open(fname) as f:
        j = json.load(f)

        if isinstance(j, list):
            j = j[0]

        if 'Points' in j:
            iomap = np.array(j['Points']).reshape(-1,4)[:,:2]
            iomap = iomap[iomap[:,0].argsort()]
            i0 = 0
            i1 = 1
            xmin = iomap[0][0]
            xmax = iomap[-1][0]
            omap = np.zeros(256)
            for i in range(256):  
                x = xmin + (i / (255.0))*(xmax - xmin)
                if (x > xmax): 
                    x = xmax;
                while iomap[i1][0] < x:
                    i0 = i0 + 1
                    i1 = i1 + 1
                d = (x - iomap[i0][0]) / (iomap[i1][0] - iomap[i0][0])
                omap[i] = (iomap[i0][1] + d * (iomap[i1][1] - iomap[i0][1]))
        else:
            omap = np.arange(256) / 255.0
            
        return omap

def load_colormap_xml(name):
    tree = ET.parse(name)
    root = tree.getroot()
    icmap = [[float(i.attrib['x']), float(i.attrib['r']), float(i.attrib['g']), float(i.attrib['b'])] for i in root.iter('Point')]
    icmap = sorted(icmap, key=lambda a: a[0])

    colormap = []

    i0 = 0
    i1 = 1

    xmin = icmap[0][0]
    xmax = icmap[-1][0]

    for i in range(256):  
        x = xmin + (i / (255.0))*(xmax - xmin)
        if (x > xmax): 
            x = xmax;

        while icmap[i1][0] < x:
            i0 = i0 + 1
            i1 = i1 + 1

        d = (x - icmap[i0][0]) / (icmap[i1][0] - icmap[i0][0])
        colormap.append([icmap[i0][i+1] + d * (icmap[i1][i+1] - icmap[i0][i+1]) for i in range(3)])

    return np.vstack(colormap).astype('f4')

def load_colormap(name):
    ext = name.split('.')[-1]
    if 'xml' == ext:
        cmap =  load_colormap_xml(name)
    elif 'json' == ext:
        cmap =  load_colormap_json(name)
    elif 'csv' == ext:
        cmap = load_colormap_csv(name)
    else:
        print('bad name:', name)
    return cmap

def load_opacitymap(name):
    ext = name.split('.')[-1]
    if 'xml' == ext:
        omap = np.arange(255)/255.0
    elif 'csv' == ext:
        omap =  np.arange(255)/255.0
    elif 'json' == ext:
        omap = load_opacitymap_json(name)
    else:
        omap = np.arange(256) / 255.0
    return omap

def interpolate_map(map, length):
    s = np.arange(length) / (length-1)
    x = np.arange(256) / 255.0
    if len(map.shape) > 1:
        return np.column_stack([np.interp(s, x, map[:,i]) for i in range(map.shape[1])])
    else:
        return np.interp(s, x, map)

def ApplyColormap2D(c,v,f):
    a = np.around(c*1023).astype('u2')
    b = np.around(v*1023).astype('u2')
    print(a.shape, b.shape, f.shape)
    return f[a,b]

def WriteColormap2D(cmap2D, filename):
    cmap2D.tofile(filename)

def ReadColormap2D(filename):
    with open(filename, 'rb') as f:
        c = np.fromfile(f, dtype='f4').reshape(1024,1024,3)
    return c

def SaveColormap(cmap, name):
    o = {}
    o["ColorSpace"] = "RGB"
    o["Name"] = name
    o["NanColor"] = [ 0, 1, 1 ]
    o["RGBPoints"] = [float(f) for f in cmap.flatten()]
    o = json.dumps([o], indent=4)
    with open('%s.json' % name, 'w') as outpt:
      outpt.write(o)




