import pdb
import pickle
import numpy as np
from glob import glob
import scipy.ndimage

class IBEX:
  def __init__(self, names = None, varnames = None, vardata = None):
    if names:
      self.resolution = vardata[0].shape[1:]
      self.names = names
      self.varnames = varnames
      self.vardata = vardata
    else:
      self.resolution = None
      self.names = []
      self.varnames = []
      self.vardata = []

  def Count(self):
      return len(self.names)

  def Add(self, name, varnames, vardata):
      if self.Count() == 0:
        self.resolution = vardata[0].shape
        self.names = [name]
        self.varnames = varnames
        self.vardata = [np.expand_dims(v, 0) for v in vardata]
      else:
        if self.Count() > 0 and vardata[0].shape != self.resolution:
          raise Exception("Data shape mismatch:", self.resolution, vardata.shape)
        self.names.append(name)
        for i,v in enumerate(varnames):
          j = self.varnames.index(v)   # be sure column names line up
          vd = vardata[i]
          self.vardata[j] = np.vstack((self.vardata[j], np.expand_dims(vd, 0)))

  def AddFromCSV(self, csv):
    name = csv.split('/')[-1].rsplit('.', 1)[0]
    lat  = []
    lon  = []
    varnames = []
    varlists = []
    varindices = []
    with open(csv) as f:
      column_names = f.readline().strip().split(',')
      for i,cn in enumerate(column_names):
        if cn == 'Lat':
          lati = i
        elif cn == 'Long': 
          loni = i
        elif cn != 'date':
          varnames.append(cn)
          varindices.append(i)
          varlists.append([])
      k = 0
      for l in f:
        l = l.strip().split(',')
        k = k + 1
        lat.append(int(l[lati].split('.')[0]))
        lon.append(int(l[loni].split('.')[0]))
        for i,j in enumerate(varindices):
          varlists[i].append(float(l[j]))
    la_min = np.min(lat)
    lat = [int((l - la_min)/2) for l in lat]
    lo_min = np.min(lon)
    lon = [int((l - lo_min)/2) for l in lon]
    data_arrays = []
    for i in range(len(varindices)):
      da = np.zeros(int(np.max(lat)+1) * int(np.max(lon)+1)).astype('f4').reshape(-1, int(np.max(lon)+1))
      for la,lo,v in zip(lat,lon,varlists[i]):
        da[la][lo] = v
      data_arrays.append(np.flipud(da))
    self.Add(name, varnames, data_arrays)

  def Write(self, file):
    f = open(file, 'wb')
    pickle.dump(self.names, f)
    pickle.dump(self.varnames, f)
    for i in range(len(self.varnames)):
      np.save(f, self.vardata[i])
    f.close()

  def Read(file):
    f = open(file, 'rb')
    names = pickle.load(f)
    varnames = pickle.load(f)
    vardata = []
    for i in range(len(varnames)):
      vardata.append(np.load(f))
    f.close()
    return IBEX(names, varnames, vardata)

  def GetByIndex(self, i):
    return [self.names[i], self.varnames, [self.vardata[j][i] for j in range(len(self.varnames))]]

  def GetByName(self, name):
    i = self.names.index(name)
    return GetByIndex(i)

  def Ranges(self):
    ranges = []
    for i in range(len(self.varnames)):
      m = np.min(self.vardata[i])
      M = np.max(self.vardata[i])
      ranges.append([m,M])
    return ranges

  def Normalize(self):
    ranges = self.Ranges()
    for i,range in enumerate(ranges):
      if (range[0] != range[1]):
        self.vardata[i] = (self.vardata[i] - range[0]) / (range[1] - range[0])

  def Resize(self, m):
    for i in range(len(self.varnames)):
      a = []
      for j in range(self.vardata[0].shape[0]):
        b = self.vardata[i][j]
        c = scipy.ndimage.zoom(b, m)
        a.append(c)
      self.vardata[i] = np.stack(a)
    self.resolution = self.vardata[0].shape[1:]
 
  def Variable(self, name):
    return self.vardata[self.varnames.index(name)]

  def Calculate(self, result_name, func):
    self.varnames.append(result_name)
    self.vardata.append(func(self))

