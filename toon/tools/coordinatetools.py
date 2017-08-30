"""Functions and classes related to coordinate system conversion"""

import numpy as np


def _shapend(args, dims=None):
    """Helper to abstract out handling shape"""
    if len(args) is 1:  # received Nx2 or 2XN array (or list)
        output = np.array(args[0], dtype='float64')
        if not dims in output.shape or len(output.shape) > dims:
            raise ValueError('Must either be N x %s or %s X N array.' % (dims, dims))
        return_array = True
        return_transpose = False
        if output.ndim > 1 and \
                        output.shape[0] is dims and \
                        output.shape[1] is not dims:
            output = output.transpose()  # act on
            return_transpose = True
    elif len(args) is dims:  # received separate x, y
        return_array = False
        return_transpose = False
        output = np.array(args[:dims], dtype='float64').transpose()
    else:
        raise ValueError('Input has incorrect dimensions.')
    return output, return_array, return_transpose


def cart2pol(*args, **kwargs):
    """Convert cartesian coordinates to polar coordinates.

    Args:
        *args: Either separate x and y in a format coercible to a numpy array,
            or a 2 by N or N by 2 array, where each row or column is a [x, y] pair.

            If given a 2 by 2 array, we assume the each row is a [x, y] pair.

        **kwargs:
            units: A string, used to specify either degrees or radians.
                Defaults to 'deg' for degrees.
            ref: A 2-element tuple or list or numpy array, which is the location of the reference
                point in cartesian coordinates. Defaults to (0, 0).

    Returns:
        [theta, radius] pairs in a format matching the input format.
    """
    units = kwargs.pop('units', 'deg')
    ref = kwargs.pop('ref', (0, 0))
    if len(ref) != 2:
        raise ValueError('Reference must be of length 2.')
    coord, return_array, return_transpose = _shapend(args, dims=2)
    if coord.ndim > 1:
        coord[:, 0:2] -= ref
        radius = np.hypot(coord[:, 0], coord[:, 1])
        theta = np.arctan2(coord[:, 1], coord[:, 0])
    else:
        coord -= ref
        radius = np.hypot(coord[0], coord[1])
        theta = np.arctan2(coord[1], coord[0])
    if units in ('deg', 'degs', 'degree', 'degrees'):
        theta *= 180.0 / np.pi
    if return_array:
        res = np.array((theta, radius))
        if return_transpose:
            return res
        return res.transpose()
    return theta, radius


def pol2cart(*args, **kwargs):
    """Convert polar coordinates to cartesian coordinates.

    Args:
        *args: Either separate theta and radius in a format coercible to a numpy array,
            or a 2 by N or N by 2 array, where each row or column is a [theta, radius] pair.

            If given a 2 by 2 array, we assume the each row is a [theta, radius] pair.

        **kwargs:
            units: A string, used to specify either degrees or radians.
                Defaults to 'deg' for degrees.
            ref: A 2-element tuple or list or numpy array, which is the location of the reference
                point in cartesian coordinates. Defaults to (0, 0).

    Returns:
        [x, y] pairs in a format matching the input format.
    """
    units = kwargs.pop('units', 'deg')
    ref = kwargs.pop('ref', (0, 0))
    if len(ref) != 2:
        raise ValueError('Reference must be of length 2.')
    coord, return_array, return_transpose = _shapend(args, dims=2)
    if units in ('deg', 'degs', 'degree', 'degrees'):
        if coord.ndim > 1:
            coord[:, 0] *= np.pi / 180.0
        else:
            coord[0] *= np.pi / 180.0
    if coord.ndim > 1:
        xx = coord[:, 1] * np.cos(coord[:, 0]) + ref[0]
        yy = coord[:, 1] * np.sin(coord[:, 0]) + ref[1]
    else:
        xx = coord[1] * np.cos(coord[0]) + ref[0]
        yy = coord[1] * np.sin(coord[0]) + ref[1]
    if return_array:
        res = np.array((xx, yy))
        if return_transpose:
            return res
        return res.transpose()
    return xx, yy


def cart2sph(*args, **kwargs):
    """Convert cartesian coordinates to spherical coordinates.

    Args:
        *args: Either separate x, y, z in a format coercible to a numpy array,
            or a 3 by N or N by 3 array, where each row or column is a [x, y, z] trio.

            If given a 3 by 3 array, we assume the each row is a [x, y, z] trio.

        **kwargs:
            units: A string, used to specify either degrees or radians.
                Defaults to 'deg' for degrees.
            ref: A 3-element tuple or list or numpy array, which is the location of the reference
                point in cartesian coordinates. Defaults to (0, 0, 0).

    Returns:
        [elevation, azimuth, radius] trios in a format matching the input format.
    """
    units = kwargs.pop('units', 'deg')
    ref = kwargs.pop('ref', (0, 0, 0))
    if len(ref) != 3:
        raise ValueError('Reference must be of length 3.')
    coord, return_array, return_transpose = _shapend(args, dims=3)
    if coord.ndim > 1:
        coord[:, 0] -= ref[0]
        coord[:, 1] -= ref[1]
        coord[:, 2] -= ref[2]
        radius = np.sqrt((coord ** 2).sum(axis=1))
        azimuth = np.arctan2(coord[:, 1], coord[:, 0])
        elevation = np.arctan2(coord[:, 2], np.sqrt(coord[:, 0] ** 2 + coord[:, 1] ** 2))
    else:
        coord[0] -= ref[0]
        coord[1] -= ref[1]
        coord[2] -= ref[2]
        radius = np.sqrt((coord ** 2).sum())
        azimuth = np.arctan2(coord[1], coord[0])
        elevation = np.arctan2(coord[2], np.sqrt(coord[0] ** 2 + coord[1] ** 2))
    if units in ('deg', 'degs', 'degree', 'degrees'):
        azimuth *= 180.0 / np.pi
        elevation *= 180.0 / np.pi
    if return_array:
        sphere = np.array([elevation, azimuth, radius])
        if return_transpose:
            return sphere
        return sphere.transpose()
    return elevation, azimuth, radius


def sph2cart(*args, **kwargs):
    """Convert spherical coordinates to cartesian coordinates.

    Args:
        *args: Either separate elevation, azimuth, radius in a format coercible to a numpy array,
            or a 3 by N or N by 3 array, where each row or column is a [elevation, azimuth, radius] trio.

            If given a 3 by 3 array, we assume the each row is a [elevation, azimuth, radius] trio.

        **kwargs:
            units: A string, used to specify either degrees or radians.
                Defaults to 'deg' for degrees.
            ref: A 3-element tuple or list or numpy array, which is the location of the reference
                point in cartesian coordinates. Defaults to (0, 0, 0).

    Returns:
        [x, y, z] trios in a format matching the input format.
    """
    units = kwargs.pop('units', 'deg')
    ref = kwargs.pop('ref', (0, 0, 0))
    if len(ref) != 3:
        raise ValueError('Reference must be of length 3.')
    coord, return_array, return_transpose = _shapend(args, dims=3)
    if coord.ndim > 1:
        if units in ('deg', 'degs', 'degree', 'degrees'):
            coord[:, 0] *= np.pi / 180.0
            coord[:, 1] *= np.pi / 180.0
        z = coord[:, 2] * np.sin(coord[:, 0]) + ref[2]
        x = coord[:, 2] * np.cos(coord[:, 0]) * np.cos(coord[:, 1]) + ref[0]
        y = coord[:, 2] * np.cos(coord[:, 0]) * np.sin(coord[:, 1]) + ref[1]
    else:
        if units in ('deg', 'degs', 'degree', 'degrees'):
            coord[0] *= np.pi / 180.0
            coord[1] *= np.pi / 180.0
        z = coord[2] * np.sin(coord[0]) + ref[2]
        x = coord[2] * np.cos(coord[0]) * np.cos(coord[1]) + ref[0]
        y = coord[2] * np.cos(coord[0]) * np.sin(coord[1]) + ref[1]
    if return_array:
        res = np.array([x, y, z])
        if return_transpose:
            return res
        return res.transpose()
    return x, y, z
