#!/usr/bin/env python
"""
GIA_uplift_ICESat_ATL15.py
Written by Tyler Sutterley (07/2026)
Calculates GIA-induced crustal uplift over polar stereographic grids for
    correcting ICESat-2 ATL15 gridded land ice height change data
Calculated directly from GIA spherical harmonics

INPUTS:
    ATL15 file(s) to read

COMMAND LINE OPTIONS:
    -h, --help: list the command line options
    -l X, --lmax X: maximum spherical harmonic degree
    -G X, --gia X: GIA model type to read
        IJ05-R2: Ivins R2 GIA Models
        W12a: Whitehouse GIA Models
        SM09: Simpson/Milne GIA Models
        ICE6G: ICE-6G GIA Models
        Wu10: Wu (2010) GIA Correction
        AW13-ICE6G: Geruo A ICE-6G GIA Models
        Caron: Caron JPL GIA Assimilation
        ICE6G-D: ICE-6G Version-D GIA Models
        ascii: reformatted GIA in ascii format
        netCDF4: reformatted GIA in netCDF4 format
        HDF5: reformatted GIA in HDF5 format
    --gia-file X: GIA file to read
    -I, --iterate: Iterations over mask to solve for large matrices
    -O X, --output-file X: output filename
    -V, --verbose: verbose output of processing run
    -M X, --mode X: Permissions mode of the files created

PYTHON DEPENDENCIES:
    numpy: Scientific Computing Tools For Python (https://numpy.org)
    h5py: Pythonic interface to the HDF5 binary data format
        (http://www.h5py.org/)
    netCDF4: Python interface to the netCDF C library
         (https://unidata.github.io/netcdf4-python/netCDF4/index.html)
    pyproj: Python interface to PROJ library
        https://pypi.org/project/pyproj/
    future: Compatibility layer between Python 2 and Python 3
        (http://python-future.org/)

PROGRAM DEPENDENCIES:
    read_GIA_model.py: reads harmonics for a glacial isostatic adjustment model
    read_love_numbers.py: reads Load Love Numbers from Han and Wahr (1995)
    clenshaw_summation.py: calculate spatial field from spherical harmonics
    gauss_weights.py: Computes the Gaussian weights as a function of degree
    harmonics.py: data class for working with spherical harmonics
    utilities.py: download and management utilities for files

REFERENCE:
    Holmes and Featherstone, "A Unified Approach to the Clenshaw Summation and
        the Recursive Computation of Very High Degree and Order Normalised
        Associated Legendre Functions", Journal of Geodesy (2002)
        http://dx.doi.org/10.1007/s00190-002-0216-2
    Tscherning and Poder, "Some Geodetic Applications of Clenshaw Summation",
        Bollettino di Geodesia e Scienze (1982)

UPDATE HISTORY:
    Updated 07/2026: use geocentric_latitude function to get the latitudes
    Updated 11/2023: can mosaic Release-3 ATL15 granules into a single grid
    Updated 09/2023: simplify input arguments
    Updated 05/2023: use pathlib to define and operate on paths
    Updated 02/2023: added iterate option to reduce memory load for 1km files
        add debug logging for ATL15 netCDF4 variables
        use love numbers class with additional attributes
    Updated 12/2022: single implicit import of gravity toolkit
    Updated 11/2022: use f-strings for formatting verbose output
    Updated 05/2022: use argparse descriptions within documentation
        use GIA reference and citation output from GIA read program
    Forked 04/2022 from calculate_GIA_uplift_ICESat2.py from Smith et al. (2020)
    Updated 04/2020: updates to reading load love numbers
    Updated 10/2019: set spatial reference using polar stereographic EPSG codes
        using pyproj for coordinate conversion
    Forked 08/2019 from gia_stereographic.py
    Updated 07/2019: added AW13 ICE6G models and option to set data directory
    Updated 06/2018: using python3 compatible octal and input
    Updated 08/2017: use clenshaw summation to calculate at each point
    Written 10/2016
"""

from __future__ import print_function

import sys
import os
import re
import time
import pyproj
import logging
import pathlib
import netCDF4
import argparse
import traceback
import numpy as np
import gravity_toolkit as gravtk
import model_harmonics as mdlhmc


# PURPOSE: keep track of threads
def info(args):
    logger = logging.getLogger(__name__)
    logger.info(pathlib.Path(sys.argv[0]).name)
    logger.info(args)
    logger.info(f'module name: {__name__}')
    if hasattr(os, 'getppid'):
        logger.info(f'parent process: {os.getppid():d}')
    logger.info(f'process id: {os.getpid():d}')


# PURPOSE: read a variable group from ICESat-2 ATL15
def read_ATL15(infile, group='delta_h', fields=None):
    # get logger
    logger = logging.getLogger(__name__)
    # dictionary with ATL15 variables
    ATL15 = {}
    attributes = {}
    infile = pathlib.Path(infile).expanduser().absolute()
    with netCDF4.Dataset(infile, mode='r') as fileID:
        # check if reading from root group or sub-group
        ncf = fileID.groups[group] if group else fileID
        # netCDF4 structure information
        logger.debug(fileID.filepath())
        logger.debug(list(ncf.variables.keys()))
        for key in fields or ncf.variables.keys():
            val = ncf.variables[key]
            ATL15[key] = val[:]
            attributes[key] = {}
            for att_name in val.ncattrs():
                attributes[key][att_name] = val.getncattr(att_name)
    # return the data and attributes
    return (ATL15, attributes)


# PURPOSE: calculate spatial fields of GIA crustal uplift to correct
# ICESat-2 ATL15 Gridded Land Ice Height Change data
def ATL15_uplift(
    filename,
    LMAX,
    GIA=None,
    GIA_FILE=None,
    OUTPUT_FILE=None,
    ITERATIONS=1,
    MODE=0o775,
):
    """
    Calculate spatial fields of GIA crustal uplift to correct
    ICESat-2 ATL15 Gridded Land Ice Height Change data following
    :cite:p:`Wahr:2000ek`

    Parameters
    ----------
    filename: str
        full path to ATL15 gridded land ice height change file
    LMAX: int
        Maximum degree and order of spherical harmonics
    GIA: str or NoneType, default None
        GIA model type to read and output

        * ``'IJ05-R2'``: Ivins R2 GIA Models :cite:p:`Ivins:2013cq`
        * ``'W12a'``: Whitehouse GIA Models :cite:p:`Whitehouse:2012jj`
        * ``'SM09'``: Simpson/Milne GIA Models :cite:p:`Simpson:2009hg`
        * ``'ICE6G'``: ICE-6G GIA Models :cite:p:`Peltier:2015bo`
        * ``'Wu10'``: Wu (2010) GIA Correction :cite:p:`Wu:2010dq`
        * ``'AW13-ICE6G'``: Geruo A ICE-6G GIA Models :cite:p:`A:2013kh`
        * ``'AW13-IJ05'``: Geruo A IJ05-R2 GIA Models :cite:p:`A:2013kh`
        * ``'Caron'``: Caron JPL GIA Assimilation :cite:p:`Caron:2018ba`
        * ``'ICE6G-D'``: ICE-6G Version-D GIA Models :cite:p:`Peltier:2018dp`
        * ``'ascii'``: reformatted GIA in ascii format
        * ``'netCDF4'``: reformatted GIA in netCDF4 format
        * ``'HDF5'``: reformatted GIA in HDF5 format
    GIA_FILE: str or NoneType, default None
        full path to input GIA file
    OUTPUT_FILE: str or NoneType, default None
        output filename for GIA uplift
    ITERATE: bool, default False
        Iterate over mask to solve for large matrices
    MODE: oct, default 0o775
        Permissions mode of output files
    """
    # parse ATL15 file
    pattern = r'(ATL\d{2})_(.*?)_(\d{2})(\d{2})_(.*?)_(\d{3})_(\d{2}).nc$'
    rx = re.compile(pattern, re.VERBOSE)

    # create mosaic of ATL15 data
    mosaic = mdlhmc.spatial.mosaic()
    # iterate over each ATL15 file
    for f in filename:
        # verify path to input ATL15 file
        f = pathlib.Path(f).expanduser().absolute()
        PRD, RGN, SCYC, ECYC, RES, RL, VERS = rx.findall(f.name).pop()
        DIRECTORY = pathlib.Path(f.parent).expanduser().absolute()
        # get ATL15 dimension variables from group
        d, attrib = read_ATL15(f, group='delta_h', fields=['x', 'y', 'time'])
        # update the mosaic grid spacing
        mosaic.update_spacing(d['x'], d['y'])
        mosaic.update_bounds(d['x'], d['y'])

    # dimensions of output mosaic
    ny, nx = mosaic.shape
    nt = len(d['time'])
    # create output mosaic
    ATL15 = {}
    ATL15['x'] = np.copy(mosaic.x)
    ATL15['y'] = np.copy(mosaic.y)
    ATL15['time'] = np.copy(d['time'])
    valid_mask = np.zeros((nt, ny, nx), dtype=bool)
    for key in ['delta_h', 'delta_h_sigma', 'ice_area']:
        ATL15[key] = np.ma.zeros((nt, ny, nx))
    # iterate over each ATL15 file
    for f in filename:
        # get ATL15 variables from group
        d, attrib = read_ATL15(f, group='delta_h')
        # get the image coordinates of the input file
        iy, ix = mosaic.image_coordinates(d['x'], d['y'])
        valid_mask[:, iy, ix] |= True
        for key in ['delta_h', 'delta_h_sigma', 'ice_area']:
            ATL15[key].set_fill_value(attrib[key]['_FillValue'])
            ATL15[key][:, iy, ix] = d[key][...]

    # update masks for variables
    for key in ['delta_h', 'delta_h_sigma', 'ice_area']:
        val = ATL15[key]
        val.mask = (
            (val.data == val.fill_value)
            | np.isnan(val.data)
            | np.logical_not(valid_mask)
        )
        val.data[val.mask] = val.fill_value

    # get attributes
    grid_mapping_name = attrib['delta_h']['grid_mapping']
    crs_wkt = attrib[grid_mapping_name]['crs_wkt']
    fill_value = attrib['delta_h']['_FillValue']
    # coordinate reference systems for converting from projection
    crs1 = pyproj.CRS.from_wkt(crs_wkt)
    crs2 = pyproj.CRS.from_epsg(4326)
    transformer = pyproj.Transformer.from_crs(crs1, crs2, always_xy=True)
    # dictionary of coordinate reference system variables
    cs_to_cf = crs1.cs_to_cf()
    crs_to_dict = crs1.to_dict()

    # read arrays of kl, hl, and ll Love Numbers
    # these Love numbers are not used in the GIA uplift calculation
    # but are a required input for the clenshaw summation
    LOVE = gravtk.load_love_numbers(
        LMAX, LOVE_NUMBERS=0, REFERENCE='CF', FORMAT='class'
    )

    # input GIA spherical harmonic datafiles
    GIA_Ylms_rate = gravtk.gia(lmax=LMAX).from_GIA(GIA_FILE, GIA=GIA)

    # convert x and y axes to grid
    gridx, gridy = np.meshgrid(ATL15['x'], ATL15['y'])
    gridlon, latitude_geodetic = transformer.transform(gridx, gridy)

    # WGS84 ellipsoid parameters
    # semimajor axis of the ellipsoid [m]
    a_axis = crs2.ellipsoid.semi_major_metre
    # flattening of the ellipsoid
    flat = crs2.ellipsoid.inverse_flattening**-1
    # calculate geocentric latitude and convert to degrees
    latitude_geocentric = mdlhmc.spatial.geocentric_latitude(
        gridlon,
        latitude_geodetic,
        a_axis=a_axis,
        flat=flat,
    )

    # output data and attributes dictionaries
    output_data = {}
    attributes = dict(ROOT={}, y={}, x={})
    # dictionary defining output structure
    struct = dict(
        dimensions=('y', 'x'),
        variables={
            'dhdt_gia': ('y', 'x'),
            'crs': (),
        },
    )
    # file-level attributes
    REFERENCE = f'Output from {pathlib.Path(sys.argv[0]).name}'
    attributes['ROOT']['reference'] = REFERENCE
    attributes['ROOT']['title'] = 'ATL15_GIA_Correction'
    attributes['summary'] = (
        'Glacial_Isostatic_Adjustment_Corrections_'
        'for_NASA_ICESat-2_ATL15_Gridded_Land_Ice_Height_Change_data.',
    )
    attributes['ROOT']['GDAL_AREA_OR_POINT'] = 'Area'
    attributes['ROOT']['Conventions'] = 'CF-1.6'
    today = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    attributes['ROOT']['date_created'] = today
    # add software information
    attributes['ROOT']['software_reference'] = gravtk.version.project_name
    attributes['ROOT']['software_version'] = gravtk.version.full_version
    # add geospatial and temporal attributes
    attributes['ROOT']['geospatial_lat_min'] = latitude_geodetic.min()
    attributes['ROOT']['geospatial_lat_max'] = latitude_geodetic.max()
    attributes['ROOT']['geospatial_lon_min'] = gridlon.min()
    attributes['ROOT']['geospatial_lon_max'] = gridlon.max()
    attributes['ROOT']['geospatial_lat_units'] = 'degrees_north'
    attributes['ROOT']['geospatial_lon_units'] = 'degrees_east'
    # x and y coordinate attributes
    for att_name in ['long_name', 'standard_name', 'units']:
        attributes['x'][att_name] = cs_to_cf[0][att_name]
        attributes['y'][att_name] = cs_to_cf[1][att_name]
    # coordinate reference system attributes
    attributes['crs'] = {}
    attributes['crs']['standard_name'] = 'Polar_Stereographic'
    # attributes['crs']['spatial_epsg'] = crs1.to_epsg()
    attributes['crs']['spatial_ref'] = crs1.to_wkt()
    attributes['crs']['proj4_params'] = crs1.to_proj4()
    attributes['crs']['latitude_of_projection_origin'] = crs_to_dict['lat_0']
    for att_name, att_val in crs1.to_cf().items():
        attributes['crs'][att_name] = att_val
    # GIA correction attributes
    attributes['dhdt_gia'] = {}
    attributes['dhdt_gia']['long_name'] = 'Viscoelastic Crustal Uplift'
    attributes['dhdt_gia']['model'] = str(GIA_Ylms_rate.citation)
    attributes['dhdt_gia']['description'] = str(GIA_Ylms_rate.title)
    attributes['dhdt_gia']['reference'] = str(GIA_Ylms_rate.reference)
    attributes['dhdt_gia']['coordinates'] = 'y x'
    attributes['dhdt_gia']['units'] = 'm/yr'
    attributes['dhdt_gia']['grid_mapping'] = 'crs'

    # create projection variable
    output_data['crs'] = np.byte()
    # copy x and y coordinates
    output_data['x'] = ATL15['x'].copy()
    output_data['y'] = ATL15['y'].copy()

    # find valid points (bare-ice, near-shore ocean or ground)
    if ITERATIONS > 1:
        valid_mask = np.logical_not(ATL15['delta_h'].mask)
    else:
        valid_mask = np.ones_like(ATL15['delta_h'].mask, dtype=bool)
    # indices of valid points
    indy, indx = np.nonzero(np.any(valid_mask, axis=0))
    nind = len(indy)

    # allocate for output GIA uplift
    output_data['dhdt_gia'] = np.empty((ny, nx))
    output_data['dhdt_gia'][:, :] = fill_value
    for i in range(ITERATIONS):
        ind = slice(i, nind, ITERATIONS)
        iY, iX = (indy[ind], indx[ind])
        # Converting GIA rates to crustal uplift (Wahr et al., 2000)
        # convert from cm to meters uplift
        output_data['dhdt_gia'][iY, iX] = 0.01 * gravtk.clenshaw_summation(
            GIA_Ylms_rate.clm,
            GIA_Ylms_rate.slm,
            gridlon[iY, iX],
            latitude_geocentric[iY, iX],
            LMAX=LMAX,
            RAD=0,
            UNITS=6,
            LOVE=LOVE,
            ASTYPE=np.float64,
            SCALE=1e-32,
        )

    # output file
    if OUTPUT_FILE is None:
        FILE = f'{PRD}_{RGN}_{RES}_GIA_{GIA_Ylms_rate.title}_L{LMAX:d}.nc'
        OUTPUT_FILE = DIRECTORY.joinpath(FILE)
    else:
        OUTPUT_FILE = pathlib.Path(OUTPUT_FILE).expanduser().absolute()

    # write structured data to netCDF4 file
    mdlhmc.spatial.to_netCDF4(OUTPUT_FILE, output_data, attributes, struct)
    # change the permissions level to MODE
    OUTPUT_FILE.chmod(mode=MODE)


# PURPOSE: create argument parser
def arguments():
    parser = argparse.ArgumentParser(
        description="""Calculates GIA-induced crustal uplift over polar
            stereographic grids for correcting ICESat-2 ATL15 gridded
            land ice height change data
            """,
        fromfile_prefix_chars='@',
    )
    parser.convert_arg_line_to_args = gravtk.utilities.convert_arg_line_to_args
    # command line parameters
    parser.add_argument(
        'infile',
        type=pathlib.Path,
        nargs='+',
        help='ICESat-2 ATL15 file to run',
    )
    # maximum spherical harmonic degree and order
    parser.add_argument(
        '--lmax',
        '-l',
        type=int,
        default=60,
        help='Maximum spherical harmonic degree',
    )
    # GIA model type list
    models = {}
    models['IJ05-R2'] = 'Ivins R2 GIA Models'
    models['W12a'] = 'Whitehouse GIA Models'
    models['SM09'] = 'Simpson/Milne GIA Models'
    models['ICE6G'] = 'ICE-6G GIA Models'
    models['Wu10'] = 'Wu (2010) GIA Correction'
    models['AW13-ICE6G'] = 'Geruo A ICE-6G GIA Models'
    models['Caron'] = 'Caron JPL GIA Assimilation'
    models['ICE6G-D'] = 'ICE-6G Version-D GIA Models'
    models['ascii'] = 'reformatted GIA in ascii format'
    models['netCDF4'] = 'reformatted GIA in netCDF4 format'
    models['HDF5'] = 'reformatted GIA in HDF5 format'
    # GIA model type
    parser.add_argument(
        '--gia',
        '-G',
        type=str,
        metavar='GIA',
        choices=models.keys(),
        help='GIA model type to read',
    )
    # full path to GIA file
    parser.add_argument(
        '--gia-file', type=pathlib.Path, help='GIA file to read'
    )
    # output filename
    parser.add_argument(
        '--output-file', '-O', type=pathlib.Path, help='Output filename'
    )
    # iterate over mask to solve for large matrices
    parser.add_argument(
        '--iterate',
        '-I',
        type=uint,
        default=1,
        help='Iterations over mask to solve for large matrices',
    )
    # print information about each input and output file
    parser.add_argument(
        '--verbose',
        '-V',
        action='count',
        default=0,
        help='Verbose output of run',
    )
    # permissions mode of the local directories and files (number in octal)
    parser.add_argument(
        '--mode',
        '-M',
        type=lambda x: int(x, base=8),
        default=0o775,
        help='Permissions mode of output files',
    )
    # return the parser
    return parser


def uint(x):
    """Argument parser type for positive integers"""
    x = int(x)
    if x <= 0:
        raise argparse.ArgumentTypeError('must be a positive integer')
    return x


# This is the main part of the program that calls the individual functions
def main():
    # Read the system arguments listed after the program
    parser = arguments()
    args, _ = parser.parse_known_args()

    # create logger
    loglevels = [logging.CRITICAL, logging.INFO, logging.DEBUG]
    logger = gravtk.utilities.build_logger(
        __name__, level=loglevels[args.verbose]
    )

    # try to run the analysis with listed parameters
    try:
        info(args)
        # run algorithm with parameters
        ATL15_uplift(
            args.infile,
            args.lmax,
            GIA=args.gia,
            GIA_FILE=args.gia_file,
            OUTPUT_FILE=args.output_file,
            ITERATIONS=args.iterate,
            MODE=args.mode,
        )
    except Exception as exc:
        # if there has been an error exception
        # print the type, value, and stack trace of the
        # current exception being handled
        logger.critical(f'process id {os.getpid():d} failed')
        logger.error(traceback.format_exc())


# run main program
if __name__ == '__main__':
    main()
