#!/usr/bin/env python
"""
spatial.py
Written by Tyler Sutterley (07/2026)
Functions for reading, writing and processing spatial data
Extends gravity_toolkit spatial module adding raster support

PYTHON DEPENDENCIES:
    spatial.py: spatial data class for reading, writing and processing data

UPDATE HISTORY:
    Updated 09/2026: added reader for structured netCDF4 files
        can write structured netCDF4 files with hierarchical groups
    Updated 07/2026: add HTML representations of mosaic and raster classes
        add geocentric_radius function to calculate the radius at coordinates
        add grib class for reading GRIB formatted data from reanalysis products
        updated scale factors for case where reference latitude is at the pole
        add writer and validation functions for structured netCDF4 files
    Updated 09/2025: use importlib to attempt to import dependencies
    Updated 06/2024: added function for calculating latitude and longitude
    Updated 04/2024: changed polar stereographic area function to scale_factors
    Updated 11/2023: add class for creating spatial mosaics
    Updated 08/2023: add function for flipping raster object
    Updated 05/2023: use pathlib to define and operate on paths
    Updated 03/2023: convert spacing and extent to raster class properties
        improve typing for variables in docstrings
        add function for calculating geocentric latitude from geodetic
    Updated 02/2023: geotiff read and write to inheritance of spatial class
    Written 10/2022
"""

import io
import copy
import time
import uuid
import logging
import pathlib
import numpy as np
import gravity_toolkit as gravtk
from model_harmonics.datum import datum
from model_harmonics.version import project_name, full_version

# attempt imports
osgeo = gravtk.utilities.import_dependency('osgeo')
osgeo.gdal = gravtk.utilities.import_dependency('osgeo.gdal')
osgeo.osr = gravtk.utilities.import_dependency('osgeo.osr')
osgeo.gdalconst = gravtk.utilities.import_dependency('osgeo.gdalconst')
netCDF4 = gravtk.utilities.import_dependency('netCDF4')
pygrib = gravtk.utilities.import_dependency('pygrib')
pyproj = gravtk.utilities.import_dependency('pyproj')


# PURPOSE: validate an existing netCDF4 file
def validate_netCDF4(filename: str | pathlib.Path, struct: dict = {}) -> bool:
    """
    Validate existing structured netCDF4 files

    Parameters
    ----------
    filename: str or pathlib.Path
        full path of input netCDF4 file
    struct: dict
        dictionary containing dimensions and variables
    """
    # get logger
    logger = logging.getLogger(__name__)
    # try to open the netCDF4 file
    try:
        # check if the file opens without corruption errors
        with netCDF4.Dataset(filename, 'r') as fileID:
            # validate netCDF4 dimensions
            for dim in struct['dimensions']:
                if dim not in fileID.dimensions:
                    logger.debug(f'Missing dimension: {dim}')
                    return False

            # validate netCDF4 variables
            for var, dimensions in struct['variables'].items():
                if var not in fileID.variables:
                    logger.debug(f'Missing variable: {var}')
                    return False
        # netCDF4 file appears to be valid
        return True
    except FileNotFoundError as exc:
        msg = f'File {str(filename)} not in file system: {exc}'
        logger.debug(msg)
        return False
    except OSError as exc:
        msg = f'File {str(filename)} is corrupt or invalid: {exc}'
        logger.debug(msg)
        return False


# PURPOSE: read a variable group from a netCDF4 file
def from_netCDF4(
    filename: str | pathlib.Path,
    struct: dict,
    mode: str = 'r',
):
    """
    Read structured data fields from a netCDF4 file

    Parameters
    ----------
    filename: str or pathlib.Path
        full path of input netCDF4 file
    struct: dict
        dictionary containing dimensions and variables
    mode: str, default 'r'
        file mode for reading netCDF4 file
    kwargs: dict
        additional keyword arguments for ``netCDF4.Dataset``

    Returns
    -------
    output: dict
        dictionary containing output data arrays
    attributes: dict
        dictionary containing file-level and variable attributes
    """
    # get logger
    logger = logging.getLogger(__name__)
    # output variable and attributes dictionaries
    output = {}
    attributes = dict(ROOT={})
    # join dimension and variables to be read
    fields = [*struct['dimensions'], *struct['variables']]
    with netCDF4.Dataset(filename, mode=mode) as fileID:
        # netCDF4 structure information
        logger.debug(fileID.filepath())
        # get root attributes
        for att_name in fileID.ncattrs():
            attributes['ROOT'][att_name] = fileID.getncattr(att_name)
        # get select variables
        for field in fields:
            # check if reading from root group or sub-group
            group, _, key = field.rpartition('/')
            ncf = fileID.groups[group] if group else fileID
            # get variable
            val = ncf.variables[key]
            output[key] = val[:]
            # get attributes
            attributes[key] = {}
            for att_name in val.ncattrs():
                attributes[key][att_name] = val.getncattr(att_name)
    # return the data and attributes
    logger.debug(list(output.keys()))
    return (output, attributes)


# PURPOSE: write structured data fields to a netCDF4 file
def to_netCDF4(
    filename: str | pathlib.Path,
    output: dict,
    attributes: dict,
    struct: dict,
    mode: str = 'w',
    **kwargs,
):
    """
    Write structured data fields to a netCDF4 file

    Parameters
    ----------
    filename: str or pathlib.Path
        full path of output netCDF4 file
    output: dict
        dictionary containing output data arrays
    attributes: dict
        dictionary containing file-level and variable attributes
    struct: dict
        dictionary containing dimensions and variables
    mode: str, default 'w'
        file mode for writing netCDF4 file
    kwargs: dict
        additional keyword arguments for ``netCDF4.Dataset``
    """
    # get logger
    logger = logging.getLogger(__name__)
    # opening netCDF4 file for writing
    filename = pathlib.Path(filename).expanduser().absolute()
    fileID = netCDF4.Dataset(filename, mode=mode, format='NETCDF4', **kwargs)
    # dictionary with netCDF4 variable objects
    nc = {}

    # defining the netCDF4 dimensions
    for dim in struct['dimensions']:
        fileID.createDimension(dim, len(output[dim]))
        nc[dim] = fileID.createVariable(dim, output[dim].dtype, (dim,))
        # add data to netCDF4 dimension variable
        nc[dim][:] = output[dim].copy()
        # set netCDF4 attributes for dimensions
        for att_name, att_val in attributes[dim].items():
            nc[dim].setncattr(att_name, att_val)

    # defining the netCDF4 variables
    for var, dimensions in struct['variables'].items():
        # check if writing to root group or sub-group
        group, _, key = var.rpartition('/')
        if group and group not in fileID.groups:
            ncf = fileID.createGroup(group)
        elif group:
            ncf = fileID.groups[group]
        else:
            ncf = fileID
        # check if output variable as fill value
        # check if output variable has dimensions
        if hasattr(output[var], 'fill_value'):
            nc[var] = ncf.createVariable(
                key,
                output[var].dtype,
                dimensions,
                fill_value=output[var].fill_value,
                zlib=True,
            )
        elif output[var].shape:
            nc[var] = ncf.createVariable(
                key,
                output[var].dtype,
                dimensions,
            )
        else:
            nc[var] = ncf.createVariable(key, output[var].dtype, ())
        # add data to netCDF4 variable
        nc[var][:] = output[var].copy()
        # set netCDF4 attributes for variables
        for att_name, att_val in attributes[var].items():
            nc[var].setncattr(att_name, att_val)

    # Defining file-level attributes
    for att_name, att_val in attributes['ROOT'].items():
        fileID.setncattr(att_name, att_val)
    # add attribute for date created
    fileID.date_created = time.strftime('%Y-%m-%d', time.localtime())
    # add software information
    fileID.software_reference = project_name
    fileID.software_version = full_version

    # Output netCDF4 structure information
    logger.info(str(filename))
    logger.info(list(fileID.variables.keys()))

    # Closing the netCDF4 file
    return fileID.close()


# PURPOSE: additional routines for the spatial module
# adding support for reading GRIB data
class grib(gravtk.spatial):
    """
    Inheritance of ``spatial`` class for reading GRIB data

    Attributes
    ----------
    data: np.ndarray
        spatial grid data
    mask: np.ndarray
        spatial grid mask
    lon: np.ndarray
        grid longitudes
    lat: np.ndarray
        grid latitudes
    fill_value: float or NoneType, default None
        invalid value for spatial grid data
    attributes: dict
        attributes of spatial variables
    """

    # inherit spatial class to read more data types
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def from_file(self, filename, **kwargs):
        """
        Read data from a GRIB file

        Parameters
        ----------
        filename: str
            full path of input GRIB file
        varname: str or NoneType, default None
            variable name to read from the GRIB file
        kwargs: dict
            additional keyword arguments for selecting GRIB messages
        """
        # get variable name to read
        varname = kwargs.pop('varname', None)
        # set filename
        if isinstance(filename, io.IOBase):
            self.filename = io.BufferedReader(filename)
        else:
            self.case_insensitive_filename(filename)
        # Open the GRIB file for reading
        self.logger.info(self.filename)
        fileID = pygrib.open(self.filename)
        # output attributes dictionary
        self.attributes['ROOT'] = {}
        # list of variable attributes
        attributes_list = [
            'cfName',
            'cfVarName',
            'missingValue',
            'name',
            'parameterName',
            'parameterUnits',
            'shortName',
            'units',
        ]
        # get dimensions and fill value
        grb = fileID.message(1)
        lat, lon = grb.latlons()
        self.fill_value = grb.missingValue
        # lon and lat are matrices
        self.lat = lat[:, 0]
        self.lon = lon[0, :]
        # dimensions shape
        nlat = len(self.lat)
        nlon = len(self.lon)
        # get projection information from GRIB message
        crs = pyproj.CRS.from_user_input(grb.projparams)
        # read messages
        if varname is not None:
            # read message with variable name
            fileID.seek(0)
            group = fileID.select(name=varname, **kwargs)
            nmessages = len(group)
        else:
            # read all messages
            group = fileID.select(**kwargs)
            nmessages = fileID.messages
        # allocate array for data
        self.data = np.zeros((nlat, nlon, nmessages))
        self.time = np.zeros((nmessages))
        self.month = np.zeros((nmessages), dtype=np.int64)
        for i, grb in enumerate(group):
            # get data values for message
            self.data[:, :, i] = grb['values']
            # save times as modified julian days (MJD)
            self.time[i] = grb.julianDay - 2400000.5
            # assign GRACE month from time
            self.month[i] = gravtk.time.calendar_to_grace(
                grb.year, month=grb.month
            )
        # set projection attributes
        self.attributes['ROOT']['projection'] = crs.to_proj4()
        self.attributes['ROOT']['wkt'] = crs.to_wkt()
        # set coordinate reference system (CRS) attributes
        cs_to_cf = crs.cs_to_cf()
        for i, key in enumerate(['lon', 'lat']):
            self.attributes[key] = {}
            for att_name, att_val in cs_to_cf[i].items():
                self.attributes[key][att_name] = att_val
        # set attributes of input variable
        self.attributes['data'] = {}
        for attr in attributes_list:
            # try getting the attribute
            try:
                self.attributes['data'][attr] = getattr(grb, attr)
            except (KeyError, ValueError, AttributeError, RuntimeError):
                pass
        # set attribute of times
        self.attributes['time'] = {}
        self.attributes['time']['units'] = 'days since 1858-11-17 00:00:00'
        self.attributes['time']['long_name'] = 'Modified Julian Day'
        self.attributes['time']['calendar'] = 'standard'
        # set mask with invalid values (0 is falsy)
        self.mask = np.zeros((nlat, nlon, nmessages), dtype=bool)
        if self.fill_value or (self.fill_value == 0):
            # mask invalid values
            self.mask[:] = self.data == self.fill_value
        # close the dataset
        fileID.close()
        self.update_mask()
        return self


# PURPOSE: additional routines for the spatial module
# for reading and writing raster data
class raster(gravtk.spatial):
    """
    Inheritance of ``spatial`` class for reading and writing
    raster data

    Attributes
    ----------
    data: np.ndarray
        spatial grid data
    mask: np.ndarray
        spatial grid mask
    x: np.ndarray
        x-coordinate array
    y: np.ndarray
        y-coordinate array
    lon: np.ndarray
        grid longitudes
    lat: np.ndarray
        grid latitudes
    fill_value: float or NoneType, default None
        invalid value for spatial grid data
    attributes: dict
        attributes of spatial variables
    extent: list, default [None,None,None,None]
        spatial grid bounds
        ``[minimum x, maximum x, minimum y, maximum y]``
    spacing: list, default [None,None]
        grid step size ``[x, y]``
    shape: tuple
        dimensions of spatial object
    ndim: int
        number of dimensions of spatial object
    filename: str
        input or output filename

    """

    np.seterr(invalid='ignore')

    # inherit spatial class to read more data types
    def __init__(self, projection=None, **kwargs):
        super().__init__(**kwargs)
        self.x = None
        self.y = None
        self.projection = projection

    def from_geotiff(self, filename, **kwargs):
        """
        Read data from a geotiff file

        Parameters
        ----------
        filename: str
            full path of input geotiff file
        compression: str or NoneType, default None
            file compression type
        bounds: list or NoneType, default bounds
            extent of the file to read:
            ``[minimum x, maximum x, minimum y, maximum y]``
        """
        # set filename
        self.case_insensitive_filename(filename)
        # set default keyword arguments
        kwargs.setdefault('compression', None)
        kwargs.setdefault('bounds', None)
        # Open the geotiff file for reading
        self.logger.info(self.filename)
        if kwargs['compression'] == 'gzip':
            # read as GDAL gzip virtual geotiff dataset
            mmap_name = f'/vsigzip/{str(self.filename)}'
            ds = osgeo.gdal.Open(mmap_name)
        elif kwargs['compression'] == 'bytes':
            # read as GDAL memory-mapped (diskless) geotiff dataset
            mmap_name = f'/vsimem/{uuid.uuid4().hex}'
            osgeo.gdal.FileFromMemBuffer(mmap_name, self.filename.read())
            ds = osgeo.gdal.Open(mmap_name)
        else:
            # read geotiff dataset
            ds = osgeo.gdal.Open(
                str(self.filename), osgeo.gdalconst.GA_ReadOnly
            )
        # get the spatial projection reference information
        srs = ds.GetSpatialRef()
        self.attributes['projection'] = srs.ExportToProj4()
        self.attributes['wkt'] = srs.ExportToWkt()
        # get dimensions
        xsize = ds.RasterXSize
        ysize = ds.RasterYSize
        bsize = ds.RasterCount
        # get geotiff info
        info_geotiff = ds.GetGeoTransform()
        # get pixel spacing
        dx = info_geotiff[1]
        dy = info_geotiff[5]
        # calculate image extents
        xmin = info_geotiff[0]
        ymax = info_geotiff[3]
        xmax = xmin + (xsize - 1) * dx
        ymin = ymax + (ysize - 1) * dy
        # x and y pixel center coordinates (converted from upper left)
        x = xmin + dx / 2.0 + np.arange(xsize) * dx
        y = ymax + dy / 2.0 + np.arange(ysize) * dy
        # if reducing to specified bounds
        if kwargs['bounds'] is not None:
            # reduced x and y limits
            xlimits = (kwargs['bounds'][0], kwargs['bounds'][1])
            ylimits = (kwargs['bounds'][2], kwargs['bounds'][3])
            # Specify offset and rows and columns to read
            xoffset = int((xlimits[0] - xmin) / dx)
            yoffset = int((ymax - ylimits[1]) / np.abs(dy))
            xcount = int((xlimits[1] - xlimits[0]) / dx) + 1
            ycount = int((ylimits[1] - ylimits[0]) / np.abs(dy)) + 1
            # reduced x and y pixel center coordinates
            self.x = x[slice(xoffset, xoffset + xcount, None)]
            self.y = y[slice(yoffset, yoffset + ycount, None)]
            # read reduced image with GDAL
            self.data = ds.ReadAsArray(
                xoff=xoffset, yoff=yoffset, xsize=xcount, ysize=ycount
            )
            # reduced image extent (converted back to upper left)
            xmin = np.min(self.x) - dx / 2.0
            xmax = np.max(self.x) - dx / 2.0
            ymin = np.min(self.y) - dy / 2.0
            ymax = np.max(self.y) - dy / 2.0
        else:
            # x and y pixel center coordinates
            self.x = np.copy(x)
            self.y = np.copy(y)
            # read full image with GDAL
            self.data = ds.ReadAsArray()
        # image extent
        self.attributes['extent'] = (xmin, xmax, ymin, ymax)
        # check if image has fill values
        self.mask = np.zeros_like(self.data, dtype=bool)
        # get invalid value (0 is falsy)
        self.fill_value = ds.GetRasterBand(1).GetNoDataValue()
        if self.fill_value or (self.fill_value == 0):
            # mask invalid values
            self.mask[:] = self.data == self.fill_value
        # close the dataset
        ds = None
        self.update_mask()
        return self

    def to_geotiff(self, filename, **kwargs):
        """
        Write a spatial object to a geotiff file

        Parameters
        ----------
        filename: str
            full path of output geotiff file
        driver: str, default 'cog'
            GDAL driver

                - ``'GTiff'``: GeoTIFF
                - ``'cog'``: Cloud Optimized GeoTIFF
        dtype: obj, default osgeo.gdal.GDT_Float64
            GDAL data type
        options: list, default ['COMPRESS=LZW']
            GDAL driver creation options
        """
        # set filename
        self.filename = pathlib.Path(filename).expanduser().absolute()
        # set default keyword arguments
        kwargs.setdefault('driver', 'GTiff')
        kwargs.setdefault('dtype', osgeo.gdal.GDT_Float64)
        kwargs.setdefault('options', ['COMPRESS=LZW'])
        # verify grid dimensions to be iterable
        self.expand_dims()
        # grid shape
        ny, nx, nband = np.shape(self.data)
        # output as geotiff or specified driver
        driver = osgeo.gdal.GetDriverByName(kwargs['driver'])
        # set up the dataset with creation options
        ds = driver.Create(
            str(self.filename),
            nx,
            ny,
            nband,
            kwargs['dtype'],
            kwargs['options'],
        )
        # top left x, w-e pixel resolution, rotation
        # top left y, rotation, n-s pixel resolution
        xmin, xmax, ymin, ymax = self.attributes['extent']
        dx, dy = self.spacing
        ds.SetGeoTransform([xmin, dx, 0, ymax, 0, dy])
        # set the spatial projection reference information
        srs = osgeo.osr.SpatialReference()
        srs.ImportFromWkt(self.attributes['wkt'])
        # export
        ds.SetProjection(srs.ExportToWkt())
        # for each band
        for band in range(nband):
            # set fill value for band (0 is falsy)
            if self.fill_value or (self.fill_value == 0):
                ds.GetRasterBand(band + 1).SetNoDataValue(self.fill_value)
            # write band to geotiff array
            ds.GetRasterBand(band + 1).WriteArray(self.data[:, :, band])
        # print filename if verbose
        self.logger.info(self.filename)
        # close dataset
        ds.FlushCache()

    def get_latlon(self, srs_proj4=None, srs_wkt=None, srs_epsg=None):
        """
        Get the latitude and longitude of grid cells

        Parameters
        ----------
        srs_proj4: str or NoneType, default None
            PROJ4 projection string
        srs_wkt: str or NoneType, default None
            Well-Known Text (WKT) projection string
        srs_epsg: int or NoneType, default None
            EPSG projection code

        Returns
        -------
        longitude: np.ndarray
            longitude coordinates of grid cells
        latitude: np.ndarray
            latitude coordinates of grid cells
        """
        # set the spatial projection reference information
        if srs_proj4 is not None:
            source = pyproj.CRS.from_proj4(srs_proj4)
        elif srs_wkt is not None:
            source = pyproj.CRS.from_wkt(srs_wkt)
        elif srs_epsg is not None:
            source = pyproj.CRS.from_epsg(srs_epsg)
        else:
            source = pyproj.CRS.from_string(self.projection)
        # target spatial reference (WGS84 latitude and longitude)
        target = pyproj.CRS.from_epsg(4326)
        # create transformation
        transformer = pyproj.Transformer.from_crs(
            source, target, always_xy=True
        )
        # create meshgrid of points in original projection
        x, y = np.meshgrid(self.x, self.y)
        # convert coordinates to latitude and longitude
        self.lon, self.lat = transformer.transform(x, y)
        return self

    @property
    def spacing(self):
        """Step size of ``raster`` object ``[x, y]``"""
        return (self.x[1] - self.x[0], self.y[1] - self.y[0])

    @property
    def extent(self):
        """Bounds of ``raster`` object
        ``[minimum x, maximum x, minimum y, maximum y]``
        """
        xmin = np.min(self.x)
        xmax = np.max(self.x)
        ymin = np.min(self.y)
        ymax = np.max(self.y)
        return [xmin, xmax, ymin, ymax]

    def copy(self):
        """
        Copy a ``raster`` object to a new ``raster`` object
        """
        temp = raster(fill_value=self.fill_value)
        # copy attributes or update attributes dictionary
        if isinstance(self.attributes, list):
            setattr(temp, 'attributes', self.attributes)
        elif isinstance(self.attributes, dict):
            temp.attributes.update(self.attributes)
        # assign variables to self
        var = ['x', 'y', 'data', 'mask', 'error', 'time', 'month', 'filename']
        for key in var:
            try:
                val = getattr(self, key)
                setattr(temp, key, copy.copy(val))
            except AttributeError:
                pass
        # update mask
        temp.replace_masked()
        return temp

    def expand_dims(self):
        """
        Add a singleton dimension to a spatial object if non-existent
        """
        # output spatial with a third dimension
        if np.ndim(self.data) == 2:
            self.data = self.data[:, :, None]
            # try expanding mask variable
            try:
                self.mask = self.mask[:, :, None]
            except Exception as exc:
                pass
        # get spacing and dimensions
        self.update_mask()
        return self

    def flip(self, axis=0):
        """
        Reverse the order of data and dimensions along an axis

        Parameters
        ----------
        axis: int, default 0
            axis to reorder
        """
        # output spatial object
        temp = self.copy()
        # copy dimensions and reverse order
        if axis == 0:
            temp.y = temp.y[::-1].copy()
        elif axis == 1:
            temp.x = temp.x[::-1].copy()
        # attempt to reverse possible data variables
        for key in ['data', 'mask', 'error']:
            try:
                setattr(temp, key, np.flip(getattr(self, key), axis=axis))
            except Exception as exc:
                pass
        # update mask
        temp.update_mask()
        return temp

    def __str__(self):
        """String representation of the ``raster`` object"""
        properties = ['model_harmonics.raster']
        extent = ', '.join(map(str, self.extent))
        properties.append(f'    extent: {extent}')
        spacing = ', '.join(map(str, self.spacing))
        properties.append(f'    spacing: {spacing}')
        shape = ', '.join(map(str, self.shape))
        properties.append(f'    shape: {shape}')
        if np.any(self.month):
            properties.append(f'    start_month: {np.min(self.month)}')
            properties.append(f'    end_month: {np.max(self.month)}')
        return '\n'.join(properties)

    def __repr__(self):
        """Representation of the ``raster`` object"""
        return self.__str__()

    def _html_repr_(self):
        """HTML representation of the ``raster`` object"""
        header = 'model_harmonics.raster'
        properties = {}
        extent = ', '.join(map(str, self.extent))
        properties['extent'] = f'[{extent}]'
        spacing = ', '.join(map(str, self.spacing))
        properties['spacing'] = f'[{spacing}]'
        shape = ', '.join(map(str, self.shape))
        properties['shape'] = f'({shape})'
        if np.any(self.month):
            properties['start_month'] = np.min(self.month)
            properties['end_month'] = np.max(self.month)
        return gravtk.utilities.html_repr(header, properties)


class mosaic:
    """Utility for creating spatial mosaics"""

    def __init__(self, **kwargs):
        self.extent = [np.inf, -np.inf, np.inf, -np.inf]
        self.spacing = [None, None]
        self.fill_value = np.nan

    def update_spacing(self, x, y):
        """
        update the step size of mosaic
        """
        try:
            self.spacing = (x[1] - x[0], y[1] - y[0])
        except:
            pass
        return self

    def update_bounds(self, x, y):
        """
        update the bounds of mosaic
        """
        # check that there is data
        if not np.any(x) or not np.any(y):
            return self
        # get extent of new data
        extent = [x.min(), x.max(), y.min(), y.max()]
        if extent[0] < self.extent[0]:
            self.extent[0] = np.copy(extent[0])
        if extent[1] > self.extent[1]:
            self.extent[1] = np.copy(extent[1])
        if extent[2] < self.extent[2]:
            self.extent[2] = np.copy(extent[2])
        if extent[3] > self.extent[3]:
            self.extent[3] = np.copy(extent[3])
        return self

    def image_coordinates(self, x, y):
        """
        get the image coordinates
        """
        # check that there is data
        if not np.any(x) or not np.any(y):
            return (None, None)
        # get the image coordinates
        iy = np.array(
            (y[:, None] - self.extent[2]) / self.spacing[1], dtype=np.int64
        )
        ix = np.array(
            (x[None, :] - self.extent[0]) / self.spacing[0], dtype=np.int64
        )
        return (iy, ix)

    @property
    def dimensions(self):
        """Dimensions of the mosaic"""
        dims = [None, None]
        # calculate y dimensions with new extents
        yptp = self.extent[3] - self.extent[2]
        dims[0] = np.int64(yptp / self.spacing[1]) + 1
        # calculate x dimensions with new extents
        xptp = self.extent[1] - self.extent[0]
        dims[1] = np.int64(xptp / self.spacing[0]) + 1
        return dims

    @property
    def shape(self):
        """Shape of the mosaic"""
        return (
            self.dimensions[0],
            self.dimensions[1],
        )

    @property
    def x(self):
        """X-coordinates of the mosaic"""
        return self.extent[0] + self.spacing[0] * np.arange(self.dimensions[1])

    @property
    def y(self):
        """Y-coordinates of the mosaic"""
        return self.extent[2] + self.spacing[1] * np.arange(self.dimensions[0])

    def __str__(self):
        """String representation of the ``mosaic`` object"""
        properties = ['model_harmonics.mosaic']
        extent = ', '.join(map(str, self.extent))
        properties.append(f'    extent: {extent}')
        spacing = ', '.join(map(str, self.spacing))
        properties.append(f'    spacing: {spacing}')
        shape = ', '.join(map(str, self.shape))
        properties.append(f'    shape: {shape}')
        return '\n'.join(properties)

    def __repr__(self):
        """Representation of the ``mosaic`` object"""
        return self.__str__()

    def _html_repr_(self):
        """HTML representation of the ``mosaic`` object"""
        header = 'model_harmonics.mosaic'
        properties = {}
        extent = ', '.join(map(str, self.extent))
        properties['extent'] = f'[{extent}]'
        spacing = ', '.join(map(str, self.spacing))
        properties['spacing'] = f'[{spacing}]'
        shape = ', '.join(map(str, self.shape))
        properties['shape'] = f'({shape})'
        return gravtk.utilities.html_repr(header, properties)


# get WGS84 parameters in CGS (centimeters, grams, seconds)
_wgs84 = datum(ellipsoid='WGS84', units='CGS')


# PURPOSE: calculate the radius of an ellipsoid at a given location
def geocentric_radius(
    lon: np.ndarray,
    lat: np.ndarray,
    h: np.ndarray = 0.0,
    a_axis: float = _wgs84.a_axis,
    flat: float = _wgs84.flat,
):
    """
    Calculates the radius of an ellipsoid at a given location
    :cite:p:`Snyder:1982gf`

    Parameters
    ----------
    lon: np.ndarray,
        longitude (degrees east)
    lat: np.ndarray,
        geodetic latitude (degrees north)
    h: np.ndarray, default 0.0
        height above the ellipsoid (meters)
    a_axis: float, default 6378137.0
        semimajor axis of the ellipsoid
    flat: float, default 1.0/298.257223563
        ellipsoidal flattening

    Returns
    -------
    radius: np.ndarray
        radius of the ellipsoid at coordinates (meters)
    """
    # first numerical eccentricity
    ecc1 = np.sqrt((2.0 * flat - flat**2) * a_axis**2) / a_axis
    # geodetic latitude in radians
    latitude_geodetic_rad = np.radians(lat)
    # prime vertical radius of curvature
    N = a_axis / np.sqrt(1.0 - ecc1**2.0 * np.sin(latitude_geodetic_rad) ** 2.0)
    # calculate X, Y and Z from geodetic latitude and longitude
    X = (N + h) * np.cos(latitude_geodetic_rad) * np.cos(np.radians(lon))
    Y = (N + h) * np.cos(latitude_geodetic_rad) * np.sin(np.radians(lon))
    Z = (N * (1.0 - ecc1**2.0) + h) * np.sin(latitude_geodetic_rad)
    # calculate radius of the ellipsoid at coordinates
    return np.sqrt(X**2.0 + Y**2.0 + Z**2.0)


# PURPOSE: calculate the geocentric latitudes
def geocentric_latitude(
    lon: np.ndarray,
    lat: np.ndarray,
    h: np.ndarray = 0.0,
    a_axis: float = _wgs84.a_axis,
    flat: float = _wgs84.flat,
):
    """
    Converts from geodetic latitude to geocentric latitude for an ellipsoid
    :cite:p:`Snyder:1982gf`

    Parameters
    ----------
    lon: np.ndarray,
        longitude (degrees east)
    lat: np.ndarray,
        geodetic latitude (degrees north)
    h: np.ndarray, default 0.0
        height above the ellipsoid (meters)
    a_axis: float, default 6378137.0
        semimajor axis of the ellipsoid
    flat: float, default 1.0/298.257223563
        ellipsoidal flattening

    Returns
    -------
    geocentric_latitude: np.ndarray
        latitude intersecting the center of the Earth (degrees north)
    """
    # first numerical eccentricity
    ecc1 = np.sqrt((2.0 * flat - flat**2) * a_axis**2) / a_axis
    # geodetic latitude in radians
    latitude_geodetic_rad = np.radians(lat)
    # prime vertical radius of curvature
    N = a_axis / np.sqrt(1.0 - ecc1**2.0 * np.sin(latitude_geodetic_rad) ** 2.0)
    # calculate X, Y and Z from geodetic latitude and longitude
    X = (N + h) * np.cos(latitude_geodetic_rad) * np.cos(np.radians(lon))
    Y = (N + h) * np.cos(latitude_geodetic_rad) * np.sin(np.radians(lon))
    Z = (N * (1.0 - ecc1**2.0) + h) * np.sin(latitude_geodetic_rad)
    # calculate geocentric latitude and convert to degrees
    return np.degrees(np.arctan(Z / np.hypot(X, Y)))


def scale_factors(
    lat: np.ndarray,
    flat: float = _wgs84.flat,
    reference_latitude: float = 70.0,
    metric: str = 'area',
):
    """
    Calculates scaling factors to account for polar stereographic
    distortion including special case of at the exact pole
    :cite:p:`Snyder:1982gf`

    Parameters
    ----------
    lat: np.ndarray
        latitude (degrees north)
    flat: float, default 1.0/298.257223563
        ellipsoidal flattening
    reference_latitude: float, default 70.0
        reference latitude (true scale latitude)
    metric: str, default 'area'
        metric to calculate scaling factors

            - ``'distance'``: scale factors for distance
            - ``'area'``: scale factors for area

    Returns
    -------
    scale: np.ndarray
        scaling factors at input latitudes
    """
    if metric.lower() not in ['distance', 'area']:
        raise ValueError('Unknown metric')
    # power for scaling factors
    power = 1.0 if metric.lower() == 'distance' else 2.0
    # convert latitude to positive radians
    phi = np.radians(np.abs(lat))
    # convert reference latitude to positive radians
    phi_ref = np.radians(np.abs(reference_latitude))
    # square of the eccentricity of the ellipsoid
    # ecc2 = (1-b**2/a**2) = 2.0*flat - flat^2
    ecc2 = 2.0 * flat - flat**2
    # eccentricity of the ellipsoid
    ecc = np.sqrt(ecc2)
    # get p values following equations 17.33 and 17.35
    p = np.sqrt(np.power(1.0 + ecc, 1.0 + ecc) * np.power(1.0 - ecc, 1.0 - ecc))
    # calculate m factors using equation 12.15
    m = np.cos(phi) / np.sqrt(1.0 - ecc2 * np.sin(phi) ** 2)
    m_ref = np.cos(phi_ref) / np.sqrt(1.0 - ecc2 * np.sin(phi_ref) ** 2)
    # calculate t factors using equation 13.9
    t = np.tan(np.pi / 4.0 - phi / 2.0) / np.power(
        (1.0 - ecc * np.sin(phi)) / (1.0 + ecc * np.sin(phi)), ecc / 2.0
    )
    t_ref = np.tan(np.pi / 4.0 - phi_ref / 2.0) / np.power(
        (1.0 - ecc * np.sin(phi_ref)) / (1.0 + ecc * np.sin(phi_ref)), ecc / 2.0
    )
    # calculate scaling factors following Snyder (1982)
    # ignore divide by zero and invalid value warnings
    with np.errstate(divide='ignore', invalid='ignore'):
        # check if reference latitude is at the pole
        if np.isclose(phi_ref, np.pi / 2.0):
            # equations 17.32 and 17.33
            k = 2.0 * t / (p * m)
            # at the pole (true scale)
            k_pole = 1.0
        else:
            # equations 17.32 and 17.34
            k = (m_ref / m) * (t / t_ref)
            # at the pole from equation 17.35
            k_pole = 0.5 * m_ref * p / t_ref
        # distance and area scaling factors with special case at the pole
        scale = np.where(
            np.isclose(phi, np.pi / 2.0),
            np.power(1.0 / k_pole, power),
            np.power(1.0 / k, power),
        )
    # return the scaling factors
    return scale


def get_latlon(x, y, srs_proj4=None, srs_wkt=None, srs_epsg=None):
    """
    Get the latitude and longitude of grid cells

    Parameters
    ----------
    srs_proj4: str or NoneType, default None
        PROJ4 projection string
    srs_wkt: str or NoneType, default None
        Well-Known Text (WKT) projection string
    srs_epsg: int or NoneType, default None
        EPSG projection code

    Returns
    -------
    longitude: np.ndarray
        longitude coordinates of grid cells
    latitude: np.ndarray
        latitude coordinates of grid cells
    """
    # set the spatial projection reference information
    if srs_proj4 is not None:
        source = pyproj.CRS.from_proj4(srs_proj4)
    elif srs_wkt is not None:
        source = pyproj.CRS.from_wkt(srs_wkt)
    elif srs_epsg is not None:
        source = pyproj.CRS.from_epsg(srs_epsg)
    else:
        raise ValueError('No projection information provided')
    # target spatial reference (WGS84 latitude and longitude)
    target = pyproj.CRS.from_epsg(4326)
    # create transformation
    transformer = pyproj.Transformer.from_crs(source, target, always_xy=True)
    # create meshgrid of points in original projection
    gridx, gridy = np.meshgrid(x, y)
    # convert coordinates to latitude and longitude
    longitude, latitude = transformer.transform(gridx, gridy)
    return (longitude, latitude)
