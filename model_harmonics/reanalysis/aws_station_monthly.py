#!/usr/bin/env python
"""
aws_station_monthly.py
Written by Tyler Sutterley (09/2026)

Calculates monthly means of automatic weather station (AWS) data

COMMAND LINE OPTIONS:
    --help: list the command line options
    -D X, --directory X: Working data directory
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
    Updated 09/2026: use struct dictionary to define netCDF4 parameters
        add standard errors about mean to the output netCDF4 files
    Updated 01/2020: don't use a smoothing factor in spline interpolation
    Updated 10/2019: check each variable if above threshold
    Written 10/2018
"""

from __future__ import print_function

import sys
import os
import re
import copy
import logging
import pathlib
import argparse
import numpy as np
import scipy.interpolate
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


def monthly_means(JD, var):
    # convert Julian dates to calendar
    YY, MM, DD, hh, mm, ss = gravtk.time.convert_julian(JD, format='tuple')
    dpm = gravtk.time.calendar_days(YY[0])
    # allocate for output data
    output = np.full((1, 12), np.nan)
    stderr = np.full((1, 12), np.nan)
    percent = np.zeros((1, 12))
    for m in range(12):
        # find data for month
        inmonth = MM == (m + 1)
        valid = np.isfinite(var[0, :]) & inmonth
        count = np.sum(valid)
        # total number of possible points in month
        total = dpm[m] / np.abs(JD[1] - JD[0])
        if count > 0:
            # calculate percent coverage
            percent[0, m] = 100.0 * count / total
            # calculate mean of atmospheric parameters
            output[0, m] = np.mean(var[0, valid])
            # calculate standard error of the mean
            stderr[0, m] = np.std(var[0, valid]) / np.sqrt(count)
    # return the monthly mean and standard errors about mean
    return output, stderr, percent


# PURPOSE: calculate the monthly mean temperature, humidity and pressure
def aws_station_monthly(
    base_dir,
    PROVIDER='AMRDC',
    YEAR=None,
    MODE=0o775,
):
    # get logger
    logger = logging.getLogger(__name__)
    # directory setup
    base_dir = pathlib.Path(base_dir).expanduser().absolute()

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
    for var in variables:
        struct['variables'][var] = ('station', 'time')
    # regular expression pattern for parsing files
    rx = re.compile(rf'{PROVIDER}_AWS_(?!Tave_)(.*?)_(\d+)\.nc$', re.I)

    # find directories to run
    directories = [d for d in base_dir.iterdir() if re.match(r'\d+', d.name)]
    # reduce list of directories to only those for the requested years
    if YEAR is not None:
        # compile regular expression operators
        years = sorted(map(str, YEAR))
        directories = [d for d in directories if d.name in years]

    # for each year to run
    for d in sorted(directories):
        # find station data
        files = [f for f in d.iterdir() if rx.match(f.name)]
        # for each file
        for f in files:
            logger.debug(f)
            # read structured netCDF4 file
            name, year = rx.findall(f.name).pop()
            dinput, attributes = mdlhmc.spatial.from_netCDF4(f, struct)
            # get epoch for converting dates
            epoch, to_sec = gravtk.time.parse_date_string(
                attributes['time']['units']
            )
            # calculate Julian day by converting to MJD and adding offset
            JD = 2400000.5 + gravtk.time.convert_delta_time(
                to_sec * dinput['time'],
                epoch1=epoch,
                epoch2=(1858, 11, 17, 0, 0, 0),
                scale=1.0 / 86400.0,
            )
            # create output dictionary
            output = {}
            output['station'] = dinput['station'].astype('|S')
            for key in ['elev', 'lat', 'lon']:
                output[key] = dinput[key].copy()
            # calculate output time
            dpm = gravtk.time.calendar_days(int(year))
            padded = np.pad(dpm, 1, mode='constant', constant_values=0)
            cumulative_days = np.cumsum(padded[:12]).astype('timedelta64[D]')
            Tave = np.datetime64(f'{year}-01-15') + cumulative_days
            # convert datetimes to delta times
            output['time'] = gravtk.time.convert_datetime(Tave, epoch=epoch)
            # copy the structure dictionary for output
            mapping = copy.deepcopy(struct)
            # for each output variable (observed and derived)
            for var in variables:
                # calculate monthly means and standard errors
                output[var], stderr, percent = monthly_means(JD, dinput[var])
                # copy standard error variables to output
                output[f'sigmas/{var}'] = stderr.copy()
                # copy attributes and update variable long name
                attributes[f'sigmas/{var}'] = copy.deepcopy(attributes[var])
                long_name = attributes[var].get('long_name', 'variable')
                attributes[f'sigmas/{var}']['long_name'] = (
                    f'standard error in {long_name} about mean'
                )
                # update the output structure dictionary to add stderr
                mapping['variables'][f'sigmas/{var}'] = ('station', 'time')
                # copy percent coverage to output variables
                output[f'coverage/{var}'] = percent.copy()
                attributes[f'coverage/{var}'] = dict(
                    units='%', long_name=f'temporal coverage of {var}'
                )
                mapping['variables'][f'coverage/{var}'] = ('station', 'time')
            # output data to netCDF4 file
            filename = d.joinpath(f'{PROVIDER}_AWS_Tave_{name}_{year}.nc')
            logger.info(filename)
            # write data to netCDF4 file
            mdlhmc.spatial.to_netCDF4(
                filename, output, attributes, mapping, mode='w'
            )
            # change the permissions mode
            filename.chmod(mode=MODE)


# PURPOSE: create argument parser
def arguments():
    parser = argparse.ArgumentParser(
        description="""Calculates monthly means of automatic weather
            station (AWS) data
            """,
        fromfile_prefix_chars='@',
    )
    parser.convert_arg_line_to_args = gravtk.utilities.convert_arg_line_to_args
    # working data directory
    parser.add_argument(
        '--directory',
        '-D',
        type=pathlib.Path,
        default=pathlib.Path.cwd(),
        help='Working data directory',
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
    aws_station_monthly(
        args.directory,
        PROVIDER=args.provider,
        YEAR=args.year,
        MODE=args.mode,
    )


# run main program
if __name__ == '__main__':
    main()
