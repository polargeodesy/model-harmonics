#!/usr/bin/env python
"""
compare_weather_stations.py
Written by Tyler Sutterley (09/2026)

Calculates differences between reanalysis surface pressures and the
    monthly mean surface pressures from weather stations

https://www.wmo.int/pages/prog/www/IMOP/meetings/SI/ET-Stand-1/Doc-10_Pressure-red.pdf
https://library.wmo.int/doc_num.php?explnum_id=3150
Wallace and Hobbs, Atmospheric Science: An Introductory Survey (2006)

Reanalysis models:
    ERA-Interim:
        http://apps.ecmwf.int/datasets/data/interim-full-moda
    ERA5:
        http://apps.ecmwf.int/data-catalogues/era5/?class=ea
    MERRA-2:
        https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/
    NCEP-DOE-2:
        https://psl.noaa.gov/data/gridded/data.ncep.Reanalysis2.html
    NCEP-CFSR:
        https://gdex.ucar.edu/datasets/d093002/
        https://gdex.ucar.edu/datasets/d094002/
    JRA-55:
        https://gdex.ucar.edu/datasets/d628000/
        http://jra.kishou.go.jp/JRA-55/index_en.html
    JRA-3Q:
        https://gdex.ucar.edu/datasets/d640000/
        https://www.data.jma.go.jp/jra/html/JRA-3Q/index_en.html

COMMAND LINE OPTIONS:
    --help: list the command line options
    -D X, --directory X: Working data directory
    -A X, --aws-directory X: Working data directory for AWS data
    -P X, --provider X: AWS data provider
    -Y X, --year X: years to run
    -V, --verbose: Output information for each output file
    -M X, --mode X: Permission mode of directories and files

PYTHON DEPENDENCIES:
    numpy: Scientific Computing Tools For Python
        https://numpy.org
        https://numpy.org/doc/stable/user/numpy-for-matlab-users.html
    netCDF4: Python interface to the netCDF C library
        https://unidata.github.io/netcdf4-python/netCDF4/index.html

PROGRAM DEPENDENCIES:
    utilities.py: download and management utilities for files

UPDATE HISTORY:
    Updated 10/2026: use struct dictionary to define netCDF4 parameters
    Written 01/2020
"""

from __future__ import print_function

import sys
import os
import re
import copy
import logging
import pathlib
import netCDF4
import argparse
import numpy as np
import gravity_toolkit as gravtk
import model_harmonics as mdlhmc
from geoid_toolkit.interpolate import Interpolate


# PURPOSE: keep track of threads
def info(args):
    logger = logging.getLogger(__name__)
    logger.info(pathlib.Path(sys.argv[0]).name)
    logger.info(args)
    logger.info(f'module name: {__name__}')
    if hasattr(os, 'getppid'):
        logger.info(f'parent process: {os.getppid():d}')
    logger.info(f'process id: {os.getpid():d}')


def expected_pressure(Z, H, T, P, Ev, Tv):
    """
    Derive expected pressure using hypsometric equation

    Parameters
    ----------
    Z: float
        Elevation
    H: float
        Orthometric height
    T: np.ndarray
        Air temperature
    P: np.ndarray
        Surface pressure
    Ev: np.ndarray
        Vapor pressure
    Tv: np.ndarray
        Virtual temperature

    Returns
    -------
    Pexp: np.ndarray
        Expected pressure
    """
    # invariant parameters
    # standard acceleration of gravity
    gamma = 9.80665
    # gas constant of dry air [J/kg/K]
    Rd = 287.05
    # average lapse rate of air [K/gpm]
    LRave = 0.0065
    # dry adiabatic lapse rate of air [k/gpm]
    LRdry = 0.0098
    # temperature change relative to a change in pressure
    # 0.12 K/hPa
    Ch = 0.12
    # characteristic gas constant of dry air
    Rc = 29.27
    # temperature in kelvin
    Tk = T + 273.15
    # height change from station elevation to model orthometric height
    dZ = Z - H
    # use dry-adiabatic lapse rate for most stations
    # use average adiabatic lapse rate for low-level stations
    # set reduction constant for low-level stations
    if Z > 50:
        LRadj = LRdry * dZ / 2.0
        Padj = np.copy(P)
    else:
        LRadj = LRave * dZ / 2.0
        Padj = P * (1.0 + dZ / (Rc * Tv))
    # expected pressure for station at model orthometric height
    Pexp = Padj * np.exp((gamma * dZ) / (Rd * (Tk + LRadj + Ev * Ch)))
    return Pexp


# PURPOSE: calculate the monthly mean temperature, humidity and pressure
def compare_weather_stations(
    base_dir,
    MODEL=None,
    DIRECTORY=None,
    PROVIDER='AMRDC',
    YEAR=None,
    RANGE=None,
    MODE=0o775,
):
    # get logger
    logger = logging.getLogger(__name__)

    # directory setup
    base_dir = pathlib.Path(base_dir).expanduser().absolute()
    ddir = base_dir.joinpath(MODEL)

    # set model specific parameters
    if MODEL == 'ERA-Interim':
        # mean file from calculate_mean_pressure.py
        input_mean_file = 'ERA-Interim-Mean-SP-{0:4d}-{1:4d}.nc'
        # invariant parameters file
        input_invariant_file = 'ERA-Interim-Invariant-Parameters.nc'
        # regular expression pattern for finding files
        regex_pattern = r'ERA\-Interim\-Monthly\-SP\-({0})\.nc$'
        VARNAME = 'sp'
        ZNAME = 'z'
        LONNAME = 'longitude'
        LATNAME = 'latitude'
        TIMENAME = 'time'
        ELLIPSOID = 'WGS84'
        GRAVITY = 9.80665
    elif MODEL == 'ERA5':
        # mean file from calculate_mean_pressure.py
        input_mean_file = 'ERA5-Mean-SP-{0:4d}-{1:4d}.nc'
        # invariant parameters file
        input_invariant_file = 'ERA5-Invariant-Parameters.nc'
        # regular expression pattern for finding files
        regex_pattern = r'ERA5\-Monthly\-SP\-({0})\.nc$'
        VARNAME = 'sp'
        ZNAME = 'z'
        LONNAME = 'longitude'
        LATNAME = 'latitude'
        TIMENAME = 'valid_time'
        ELLIPSOID = 'WGS84'
        GRAVITY = 9.80665
    elif MODEL == 'MERRA-2':
        # mean file from calculate_mean_pressure.py
        input_mean_file = 'MERRA2.Mean_PS.{0:4d}-{1:4d}.nc'
        # invariant parameters file
        input_invariant_file = 'MERRA2_101.const_2d_asm_Nx.00000000.nc4'
        # regular expression pattern for finding files
        regex_pattern = (
            r'MERRA2_\d{{3}}.tavgM_2d_slv_Nx.({0})(\d{{2}}).(.*?).nc$'
        )
        VARNAME = 'PS'
        ZNAME = 'PHIS'
        LONNAME = 'lon'
        LATNAME = 'lat'
        TIMENAME = 'time'
        ELLIPSOID = 'WGS84'
        GRAVITY = 9.80665
    elif MODEL == 'NCEP-DOE-2':
        # mean file from calculate_mean_pressure.py
        input_mean_file = 'pres.sfc.mean.{0:4d}-{1:4d}.nc'
        # invariant parameters file
        input_invariant_file = 'hgt.sfc.nc'
        # regular expression pattern for finding files
        regex_pattern = r'pres.sfc.mon.mean.({0}).nc$'
        VARNAME = 'pres'
        ZNAME = 'hgt'
        LONNAME = 'lon'
        LATNAME = 'lat'
        TIMENAME = 'time'
        ELLIPSOID = 'WGS84'
        # NCEP-DOE-2 reanalysis geopotential heights are already in meters
        GRAVITY = 1.0
    elif MODEL == 'NCEP-CFSR':
        # mean file from calculate_mean_pressure.py
        input_mean_file = 'splanl.mean.gdas.{0:4d}-{1:4d}.nc'
        # invariant parameters file
        input_invariant_file = 'hgt.gdas.nc'
        # regular expression pattern for finding files
        regex_pattern = r'splanl.gdas.({0})(\d+).nc$'
        VARNAME = 'ave_sp'
        ZNAME = 'orog'
        LONNAME = 'lon'
        LATNAME = 'lat'
        TIMENAME = 'time'
        ELLIPSOID = 'WGS84'
        # NCEP-CFSR reanalysis geopotential heights are already in meters
        GRAVITY = 1.0
    elif MODEL == 'JRA-55':
        # mean file from calculate_mean_pressure.py
        input_mean_file = 'anl_surf.001_pres.mean.{0:4d}-{1:4d}.nc'
        # invariant parameters file
        input_invariant_file = 'll125.006_gp.2000.nc'
        # regular expression pattern for finding files
        regex_pattern = r'anl_surf125\.001_pres\.({0})(\d+).nc$'
        VARNAME = 'sp'
        ZNAME = 'z'
        LONNAME = 'lon'
        LATNAME = 'lat'
        TIMENAME = 'time'
        ELLIPSOID = 'WGS84'
        GRAVITY = 9.80665
    elif MODEL == 'JRA-3Q':
        # mean file from calculate_mean_pressure.py
        input_mean_file = 'jra3q.mean.pres-sfc-an-gauss.{0:4d}-{1:4d}.nc'
        # invariant parameters file
        input_invariant_file = (
            'jra3q.tl479_surf.0_3_4.gp-sfc-cn-gauss.1947090100_1947090100.nc'
        )
        # regular expression pattern for finding files
        regex_pattern = r'jra3q\.anl_surf\.pres-sfc-an-gauss\.({0})(\d+).nc$'
        VARNAME = 'pres-sfc-an-gauss'
        ZNAME = 'gp-sfc-cn-gauss'
        LONNAME = 'lon'
        LATNAME = 'lat'
        TIMENAME = 'time'
        ELLIPSOID = 'WGS84'
        GRAVITY = 9.80665

    # read mean pressure field from calculate_mean_pressure.py
    mean_file = ddir.joinpath(input_mean_file.format(RANGE[0], RANGE[1]))
    mean_pressure, lon, lat = ncdf_mean_pressure(
        mean_file, VARNAME, LONNAME, LATNAME
    )
    nlat, nlon = np.shape(mean_pressure)
    # required order of dimensions
    dimensions = [TIMENAME, LATNAME, LONNAME]
    # calculate meshgrid from latitude and longitude
    gridlon, gridlat = np.meshgrid(lon, lat)
    gridtheta = np.radians(90.0 - gridlat)

    # read model orography from invariant parameters file
    geopotential = ncdf_invariant(ddir.joinpath(input_invariant_file), ZNAME)
    # convert geopotential to orography (above mean sea level)
    # https://software.ecmwf.int/wiki/x/WAfEB
    geopotential_height = geopotential / GRAVITY
    # orthometric height from List (1958) as described in Boy and Chao (2005)
    cos2th = np.cos(2.0 * gridtheta)
    orthometric = ((1.0 - 0.002644 * cos2th) * geopotential_height) + (
        (1.0 - 0.0089 * cos2th) * (geopotential_height**2) / 6.245e6
    )

    # variables of interest
    variables = ['air_temp', 'pressure', 'rh']
    # append derived variables
    if PROVIDER in ('AMRDC',):
        derived = [
            'dew_temp',
            'mix_ratio',
            'mslp',
            'sh',
            'vapor_pressure',
            'virtual_temp',
        ]
        variables.extend(derived)

    # netCDF4 structure
    struct = dict(dimensions=('time', 'station'), variables={})
    struct['variables']['elev'] = ('station',)
    struct['variables']['lat'] = ('station',)
    struct['variables']['lon'] = ('station',)
    mapping = copy.deepcopy(struct)
    for var in variables:
        struct['variables'][var] = ('station', 'time')
    # output netCDF4 structure
    mapping['variables']['sp'] = ('station', 'time')
    mapping['variables']['p_expected'] = ('station', 'time')
    mapping['variables']['p_diff'] = ('station', 'time')
    mapping['variables']['h_ortho'] = ('station',)
    # regular expression pattern for parsing averaged files
    rx1 = re.compile(rf'{PROVIDER}_AWS_Tave_(.*?)_(\d+)\.nc$', re.I)

    # find directories to run
    DIRECTORY = pathlib.Path(DIRECTORY).expanduser().absolute()
    directories = [d for d in DIRECTORY.iterdir() if re.match(r'\d+', d.name)]
    # reduce list of directories to only those for the requested years
    if YEAR is not None:
        # compile regular expression operators
        years = sorted(map(str, YEAR))
        directories = [d for d in directories if d.name in years]

    # for each year to run
    for d in sorted(directories):
        # find station data
        files = [f for f in d.iterdir() if rx1.match(f.name)]
        # find reanalysis files for year
        rx2 = re.compile(regex_pattern.format(d.name), re.VERBOSE)
        input_list = sorted([f for f in ddir.iterdir() if rx2.match(f.name)])
        # skip if there are no reanalysis files for the year
        if not input_list:
            continue

        # read reanalysis surface pressure values for the year
        m = 0
        pressure = np.zeros((12, nlat, nlon))
        # for each reanalysis file
        for i, input_file in enumerate(input_list):
            # read input data
            logger.debug(str(input_file))
            with netCDF4.Dataset(input_file, mode='r') as fileID:
                # check dimensions for expver slice
                if fileID.variables[VARNAME].ndim == 4:
                    var = ncdf_expver(fileID, VARNAME)
                else:
                    var = fileID.variables[VARNAME][:].copy()
                # update mask variable
                fill_value = fileID.variables[VARNAME]._FillValue
                var = np.ma.masked_equal(var, fill_value)
                # reorder dimensions to match the required order
                dims = fileID.variables[VARNAME].dimensions
                order = [dims.index(d) for d in dimensions]
                var = var.transpose(order)
                nt, _, _ = var.shape
                pressure[m : m + nt, :, :] = var
                m += nt

        # create interpolation object for surface pressure
        interp = Interpolate((lat, lon), method='linear')
        # for each station file
        for f in files:
            logger.debug(f)
            # read structured netCDF4 file
            name, year = rx1.findall(f.name).pop()
            dinput, attributes = mdlhmc.spatial.from_netCDF4(f, struct)
            # create output dictionary
            output = {}
            output['station'] = dinput['station'].astype('|S')
            for key in ['elev', 'lat', 'lon', 'time']:
                output[key] = dinput[key].copy()
            # update attributes
            attributes['sp'] = {}
            attributes['sp']['units'] = 'hPa'
            attributes['sp']['long_name'] = 'surface_pressure'
            attributes['p_diff'] = {}
            attributes['p_diff']['units'] = 'hPa'
            attributes['p_diff']['long_name'] = 'pressure_difference'
            attributes['p_expected'] = {}
            attributes['p_expected']['units'] = 'hPa'
            attributes['p_expected']['long_name'] = 'expected_pressure'
            attributes['h_ortho'] = {}
            attributes['h_ortho']['units'] = 'm'
            attributes['h_ortho']['long_name'] = 'orthometric_height'

            # calculate mean pressure over same time range
            total = 0.0
            count = 0
            for Y in range(RANGE[0], RANGE[1] + 1):
                dm = DIRECTORY.joinpath(str(Y))
                fm = dm.joinpath(f'{PROVIDER}_AWS_Tave_{name}_{Y:4d}.nc')
                if fm.exists():
                    m, a = mdlhmc.spatial.from_netCDF4(fm, struct)
                    total += a['pressure']['mean'] * a['pressure']['count']
                    count += a['pressure']['count']
            # calculate mean
            if count > 0:
                aws_mean = total / count

            # interpolate reanalysis surface pressure to station
            sp = np.zeros((1, 12))
            diff = np.zeros((1, 12))
            expected = np.zeros((1, 12))
            # interpolate mean pressure to station
            interp.update(mean_pressure)
            sp_mean = 0.01 * interp((dinput['lat'], dinput['lon']))
            attributes['sp']['mean'] = sp_mean
            attributes['sp']['aws_mean'] = aws_mean
            attributes['sp']['aws_count'] = count
            # interpolate orthometric height to station
            interp.update(orthometric)
            ortho = interp((dinput['lat'], dinput['lon']))
            for m in range(12):
                interp.update(pressure[m, :, :] - mean_pressure)
                sp[:, m] = 0.01 * interp((dinput['lat'], dinput['lon']))
                aws_pressure = dinput['pressure'][:, m] - aws_mean
                diff[:, m] = sp[:, m] - aws_pressure
                # calculate expected pressure
                exp = expected_pressure(
                    dinput['elev'],
                    ortho,
                    dinput['air_temp'][:, m],
                    aws_pressure,
                    dinput['vapor_pressure'][:, m],
                    dinput['virtual_temp'][:, m],
                )
                expected[:, m] = exp - sp_mean
            # copy interpolated values
            output['sp'] = sp
            output['p_diff'] = diff
            output['p_expected'] = expected
            output['h_ortho'] = ortho
            # write data to netCDF4 file
            filename = f.with_name(f'{MODEL}_Tave_{name}_{year}.nc')
            logger.info(filename)
            mdlhmc.spatial.to_netCDF4(
                filename, output, attributes, mapping, mode='w'
            )
            # change the permissions mode
            filename.chmod(mode=MODE)


# PURPOSE: read reanalysis mean pressure from calculate_mean_pressure.py
def ncdf_mean_pressure(FILENAME, VARNAME, LONNAME, LATNAME):
    # get logger
    logger = logging.getLogger(__name__)
    logger.debug(str(FILENAME))
    with netCDF4.Dataset(FILENAME, mode='r') as fileID:
        mean_pressure = np.array(fileID.variables[VARNAME][:].squeeze())
        longitude = fileID.variables[LONNAME][:].squeeze()
        latitude = fileID.variables[LATNAME][:].squeeze()
    return (mean_pressure, longitude, latitude)


# PURPOSE: extract pressure variable from a 4d netCDF4 dataset
# ERA5 expver dimension (denotes mix of ERA5 and ERA5T)
def ncdf_expver(fileID, VARNAME):
    ntime, nexp, nlat, nlon = fileID.variables[VARNAME].shape
    # reduced surface pressure output
    pressure = np.zeros((ntime, nlat, nlon))
    for t in range(ntime):
        # iterate over expver slices to find valid outputs
        for j in range(nexp):
            # check if any are valid for expver
            if np.any(fileID.variables[VARNAME][t, j, :, :]):
                pressure[t, :, :] = fileID.variables[VARNAME][t, j, :, :]
    # return the reduced pressure variable
    return pressure


# PURPOSE: read reanalysis invariant parameters for geopotential
def ncdf_invariant(FILENAME, ZNAME):
    # get logger
    logger = logging.getLogger(__name__)
    logger.debug(str(FILENAME))
    with netCDF4.Dataset(FILENAME, mode='r') as fileID:
        geopotential = fileID.variables[ZNAME][:].squeeze()
    return geopotential


# PURPOSE: create argument parser
def arguments():
    parser = argparse.ArgumentParser(
        description="""Calculates differences between reanalysis surface
            pressures and monthly mean surface pressures from weather stations
            """,
        fromfile_prefix_chars='@',
    )
    parser.convert_arg_line_to_args = gravtk.utilities.convert_arg_line_to_args
    # command line parameters
    choices = [
        'ERA-Interim',
        'ERA5',
        'MERRA-2',
        'NCEP-DOE-2',
        'NCEP-CFSR',
        'JRA-55',
        'JRA-3Q',
    ]
    parser.add_argument(
        'model',
        type=str,
        metavar='MODEL',
        choices=choices,
        help='Reanalysis Model',
    )
    # working data directories
    parser.add_argument(
        '--directory',
        '-D',
        type=pathlib.Path,
        default=pathlib.Path.cwd(),
        help='Working data directory',
    )
    parser.add_argument(
        '--aws-directory',
        '-A',
        type=pathlib.Path,
        default=pathlib.Path.cwd(),
        help='Working data directory for AWS data',
    )
    # AWS data provider
    choices = ['AMRC', 'AMRDC']
    parser.add_argument(
        '--provider',
        '-P',
        type=str,
        choices=choices,
        default='AMRDC',
        help='AWS data provider',
    )
    # years to run
    parser.add_argument(
        '--year',
        '-Y',
        type=int,
        nargs='+',
        help='Years to run',
    )
    # start and end years to run for mean
    parser.add_argument(
        '--mean',
        metavar=('START', 'END'),
        type=int,
        nargs=2,
        default=[2003, 2014],
        help='Start and end year range for mean',
    )
    # print information about each input and output file
    parser.add_argument(
        '--verbose',
        '-V',
        action='count',
        default=0,
        help='Verbose output of processing run',
    )
    # permissions mode of the local directories and files (number in octal)
    parser.add_argument(
        '--mode',
        '-M',
        type=lambda x: int(x, base=8),
        default=0o775,
        help='Permission mode of directories and files',
    )
    # return the parser
    return parser


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
    # run program
    compare_weather_stations(
        args.directory,
        args.model,
        PROVIDER=args.provider,
        DIRECTORY=args.aws_directory,
        YEAR=args.year,
        RANGE=args.mean,
        MODE=args.mode,
    )


# run main program
if __name__ == '__main__':
    main()
