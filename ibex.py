import pdb
import pickle
import numpy as np
from glob import glob
import scipy.ndimage

class IBEX:
  def __init__(self, names = None, fluxes = None, errors = None):
    if names:
      self.resolution = fluxes.shape[1:]
      self.names = names
      self.fluxes = fluxes
      self.errors = errors
    else:
      self.resolution = None
      self.names = []
      self.fluxes = []
      self.errors = []

  def Count(self):
      return len(self.names)

  def Add(self, name, flux, err):
      if self.Count() > 0 and flux.shape != self.resolution:
        raise Exception("Data shape mismatch:", self.resolution, flux.shape)
      else:
        self.resolution = flux.shape
        self.names.append(name)
        self.fluxes.append(flux)
        self.errors.append(err)

  def AddFromCSV(self, csv):
    name = csv.split('/')[-1].rsplit('.', 1)[0]
    lat  = []
    lon  = []
    flux = []
    err  = []
    with open(csv) as f:
      f.readline()
      for l in f:
        l = l.strip().split(',')[:4]
        lat.append(int(l[0].split('.')[0]))
        lon.append(int(l[1].split('.')[0]))
        flux.append(float(l[2]))
        err.append(float(l[3]))
    la_min = np.min(lat)
    lat = [int((l - la_min)/2) for l in lat]
    lo_min = np.min(lon)
    lon = [int((l - lo_min)/2) for l in lon]
    farray = np.zeros(int(np.max(lat)+1) * int(np.max(lon)+1)).astype('f4').reshape(-1, int(np.max(lon)+1))
    earray = np.zeros(int(np.max(lat)+1) * int(np.max(lon)+1)).astype('f4').reshape(-1, int(np.max(lon)+1))
    for la,lo,f,e in zip(lat,lon,flux,err):
      farray[la][lo] = f
      earray[la][lo] = e
    self.Add(name, farray, earray)

  def Write(self, file):
    f = open(file, 'wb')
    pickle.dump(self.names, f)
    np.save(f, self.fluxes)
    np.save(f, self.errors)
    f.close()

  def Read(file):
    f = open(file, 'rb')
    names = pickle.load(f)
    fluxes = np.load(f)
    errors = np.load(f)
    f.close()
    return IBEX(names, fluxes, errors)

  def GetByIndex(self, i):
    return [self.names[i], self.fluxes[i], self.errors[i]]

  def GetByName(self, name):
    i = self.names.index(name)
    return GetByIndex(i)

  def Ranges(self):
    f = np.vstack(self.fluxes)
    min_f = np.min(f)
    max_f = np.max(f)
    e = np.vstack(self.errors)
    min_e = np.min(e)
    max_e = np.max(e)
    return (min_f, max_f, min_e, max_e)

  def Normalize(self):
    minf, maxf, mine, maxe = self.Ranges()
    self.errors = self.errors / self.fluxes
    self.fluxes = (self.fluxes - minf) / (maxf - minf)
    self.errors = (self.errors - mine) / (maxe - mine)

  def Resize(self, m):
    for i in range(len(self.fluxes)):
      self.fluxes[i] = scipy.ndimage.zoom(self.fluxes[i], m)
      self.errors[i] = scipy.ndimage.zoom(self.errors[i], m)
    self.resolution = self.fluxes[0].shape

