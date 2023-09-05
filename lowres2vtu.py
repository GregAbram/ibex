#! /usr/bin/env python3

import sys
import numpy as np
from glob import glob
import vtk
from vtk.numpy_interface import dataset_adapter as dsa
import pyproj 

# transformer = pyproj.Transformer.from_crs("EPSG:4326", "ESRI:54009")
# transformer = pyproj.Transformer.from_crs("EPSG:4326", "+proj=ob_tran +o_proj=moll +o_lon_p=256 +o_lat_p=85 +lon_0=0")
transformer = pyproj.Transformer.from_crs("EPSG:4326", "+proj=ob_tran +o_proj=moll +o_lon_p=-105.7 +o_lat_p=85 +lon_0=0")


for level in range(2, 7):
  vtu = dsa.WrapDataObject(vtk.vtkUnstructuredGrid())

  if 1 == 1:
    # Assign data to cell centers

    npoints = (30+1)*(60+1)
    nquads = 30*60

    i = np.arange(npoints)
    lon = 6*np.mod(i, 61) - 180
    lat = 6*np.trunc(i / 61) - 90
    vtu.Points = np.column_stack((lon, lat, [0]*npoints))

    i = np.arange(nquads).astype('i4')
    x = np.mod(i, 60)
    y = np.trunc(i / 60).astype('i4')
    p = y * 61 + x
    q = p + 1
    r = q + 61
    s = r - 1
  else:
    # Assign data to vertices

    npoints = 30*60
    nquads = (30-1)*(60-1)

    i = np.arange(npoints)
    lon = 6*np.mod(i, 60) - 180
    lat = 6*np.trunc(i / 60) - 90
    vtu.Points = np.column_stack((lon, lat, [0]*npoints))

    nquads = (30-1)*(60-1)
    i = np.arange(nquads).astype('i4')
    x = np.mod(i, 59)
    y = np.trunc(i / 59).astype('i4')
    p = y * 60 + x
    q = p + 1
    r = q + 60
    s = r - 1

  hexes = np.column_stack(([4]*nquads, p, q, r, s))
  types = np.array([vtk.VTK_QUAD]*nquads).astype('u1')
  offsets = np.arange(nquads)*5

  hexes = dsa.numpy_support.numpy_to_vtkIdTypeArray(hexes.flatten())
  types = dsa.numpy_support.numpy_to_vtk(types)
  offsets = dsa.numpy_support.numpy_to_vtkIdTypeArray(offsets)

  vcells = vtk.vtkCellArray()
  vcells.SetCells(nquads, hexes)
  vtu.VTKObject.SetCells(types, offsets, vcells)

  x,y = transformer.transform(lat, lon)
  mw_points = np.column_stack((x, y, [0]*len(x)))
  vtu.PointData.append(mw_points, 'mollweide')

  files = glob('*-%d-*txt' % level)
  files = [f for f in files if 'desc' not in f]

  for filename in files:
    name = filename.split('-')[-1].split('.')[0]
    array = None
    first = True
    with open(filename) as file:
      for line in file:
        if line[0] == '#':
          continue
        line = np.array([float(f) for f in line.strip().split()])
        if first:
          array = line
          first = False
        else:
          array = np.vstack((array, line))
    if 1 == 1:
      # Assign data to cell centers
      vtu.CellData.append(array.flatten().astype('f4'), name)
    else:
      # Assign data to vertices
      vtu.PointData.append(array.flatten().astype('f4'), name)

  wrtr = vtk.vtkXMLUnstructuredGridWriter()
  wrtr.SetFileName('level-%d.vtu' % level)
  wrtr.SetInputData(vtu.VTKObject)
  wrtr.Write()
