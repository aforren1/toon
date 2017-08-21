"""Functions and classes related to coordinate system conversion"""

import numpy as np

def _shapend(args, dims=None):
    """Helper to abstract out handling shape"""
    if len(args) == 1: # received Nx2 or 2XN array
        coord = np.asarray(args[0])
        if not dims in coord.shape or len(coord.shape) > dims:
            raise ValueError('Must either be Nx2 or 2XN array.')
        return_array = True
        return_transpose = False
        if coord.shape[0] == dims:
            coord = np.transpose(coord) # act on
            return_transpose = True
    elif len(args) == dims: # received separate x, y
        return_array = False
        return_transpose = False
        if dims == 2:
            coord = np.array((args[0], args[1])).transpose() # x,y
        elif dims == 3:
            coord = np.array((args[0], args[1], args[2])).transpose() #x,y,z
    else:
        raise ValueError('Coordinates wrong.')
    return coord, return_array, return_transpose

def cart2pol(*args, units='deg', ref=(0,0)):
    """
    *args contains either separate x, y
    or Nx2 array or 2xN array, and returns that format

    """
    if len(ref) != 2:
        raise ValueError('Reference must be of length 2.')
    coord, return_array, return_transpose = _shapend(args, 2)
    coord -= ref
    radius = np.hypot(coord[:, 0], coord[:, 1])
    theta = np.arctan2(coord[:, 1], coord[:, 0])
    if units in ('deg', 'degs', 'degree', 'degrees'):
        theta *= 180 / np.pi
    if return_array:
        res = np.asarray((theta, radius))
        if return_transpose:
            return res
        return res.transpose()
    return theta, radius

def pol2cart(*args, units='deg', ref=(0,0)):
    """
    *args is either separate theta, radius or
    Nx2 array, with [theta, radius]
    """
    if len(ref) != 2:
        raise ValueError('Reference must be of length 2.')
    coord, return_array, return_transpose = _shapend(args, 2)
    if units in ('deg', 'degs', 'degree', 'degrees'):
        coord[:, 0] *= np.pi / 180.0
    xx = coord[:, 1] * np.cos(coord[:, 0]) + ref[0]
    yy = coord[:, 1] * np.sin(coord[:, 0]) + ref[1]
    if return_array:
        res = np.asarray((xx, yy))
        if return_transpose:
            return res
        return res.transpose()
    return xx, yy

def cart2sph(*args, units='deg', ref=(0,0,0)):
    if len(ref) != 3:
        raise ValueError('Reference must be of length 3.')
    coord, return_array, return_transpose = _shapend(args, 3)
    coord -= ref
    radius = np.sqrt((coord**2).sum(axis=1))
    azimuth = np.arctan2(coord[:,1], coord[:,0])
    elevation = np.arctan2(coord[:,2],
                           np.sqrt(coord[:,0]**2 + coord[:,1]**2))
    if units in ('deg', 'degs', 'degree', 'degrees'):
        azimuth *= 180.0/np.pi
        elevation *= 180.0/np.pi
    if return_array:
        sphere = np.asarray([elevation, azimuth, radius])
        if return_transpose:
            return sphere
        return sphere.transpose()
    return azimuth, elevation, radius

def sph2cart(*args, units='deg', ref=(0,0,0)):
    if len(ref) != 3:
        raise ValueError('Reference must be of length 3.')
    coord, return_array, return_transpose = _shapend(args, 3)
    if units in ('deg', 'degs', 'degree', 'degrees'):
        coord[:, 0] *= np.pi/180.0
        coord[:, 1] *= np.pi/180.0
    z = coord[:, 2] * np.sin(coord[:, 1])
    x = coord[:, 2] * np.cos(coord[:, 1]) * np.cos(coord[:, 0])
    y = coord[:, 2] * np.cos(coord[:, 1]) * np.sin(coord[:, 0])
    if return_array:
        res = np.asarray([x, y, z])
        if return_transpose:
            return res
        return res.transpose()
    return x, y, z
