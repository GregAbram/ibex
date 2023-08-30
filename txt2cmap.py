#! /usr/bin/env python3

import sys, pdb
import colortools as ct
import numpy as np

names = ['ct39', 'ct39-ibex']

with open('cmaps.txt') as inpt:
  for n in names:
    for l in inpt:
      if 'RED' in l:
        break

    cmap = [[i] + [float(j)/255.0 for j in inpt.readline().strip().split()] for i in range(256)]
    cmap = np.array(cmap)
    pdb.set_trace()
    ct.SaveColormap(cmap, n)

    cmap = [['%f' % j for j in i] for i in cmap]
    with open('%s.csv' % n, 'w') as outpt:
      for i,c in enumerate(cmap):
        outpt.write(','.join(['%d' % i] + c) + '\n')

