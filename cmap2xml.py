import sys
from ibex import colortools as ct

cmap = ct.load_colormap(sys.argv[1])
name = sys.argv[1].split('/')[-1].split('.')[0]
ct.SaveColormapXML(cmap, name)


