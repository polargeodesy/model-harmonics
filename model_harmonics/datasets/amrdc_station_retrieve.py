#!/usr/bin/env python
"""
amrdc_station_retrieve.py
Written by Tyler Sutterley (09/2026)

Downloads automatic weather station (AWS) data from the
    Antarctic Meteorological Research and Data Center (AMRDC)
    https://amrdc.ssec.wisc.edu/
    https://amrdcdata.ssec.wisc.edu/

COMMAND LINE OPTIONS:
    --help: list the command line options
    -D X, --directory X: Working data directory
    -Y X, --year X: years to download
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
    Updated 09/2026: updated for the new data center APIs
        use struct dictionary to define netCDF4 parameters
    Updated 10/2019: python3 compatibility url request
    Updated 10/2018: can set the years to download
    Updated 06/2018: using python3 compatible octal, input and urllib
    Written 03/2018
"""

from __future__ import print_function

import sys
import os
import re
import logging
import pathlib
import argparse
import traceback
import lxml.etree
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


def build_query(station, year, query_type='all', interval='10', variable=None):
    """Build URL for fetching AWS data"""
    HOST = 'https://amrdcdata.ssec.wisc.edu/data-api/aws/data?'
    # build parameters for query
    parameters = {}
    parameters['query_type'] = query_type
    parameters['stations'] = station
    if variable is not None:
        parameters['variable'] = variable
    parameters['interval'] = str(interval)
    parameters['startdate'] = f'{year:4d}-01-01'
    parameters['enddate'] = f'{year:4d}-12-31'
    # return query url
    URL = HOST + gravtk.utilities.urlencode(parameters)
    # get logger
    logger = logging.getLogger(__name__)
    logger.debug(URL)
    # return the query URL
    return URL


def fetch_parameters(station, year, parser=None, timeout=20):
    """Get parameters for station for year"""
    HOST = f'https://amrdc.ssec.wisc.edu/aws?_year={str(year)}'
    # get logger
    logger = logging.getLogger(__name__)
    logger.debug(HOST)
    # request station list for year
    request = gravtk.utilities.urllib2.Request(url=HOST)
    response = gravtk.utilities.urllib2.urlopen(request, timeout=timeout)
    tree = lxml.etree.parse(response, parser)
    # parse table headers for variable names
    keys = tree.xpath('//table/thead/tr/th/text()')
    keys.pop(0)
    # dictionary with output station parameters
    params = {}
    # find each table row
    for tr in tree.xpath('//table/tbody/tr'):
        # find variables in the row
        variables = tr.xpath('td/a/text() | td/text()')
        key = variables.pop(0).strip()
        params[key] = {k: v for k, v in zip(keys, variables)}
    # remap parameters for some stations
    mapping = {}
    mapping['Dome-C'] = 'Dome C'
    mapping['Dome Fuji'] = 'Dome F (Fuji)'
    mapping['Kominko-Slade'] = 'Kominko-Slade (WAIS)'
    mapping['Sky Blu'] = 'Sky-Blu'
    # first try remapped cases
    # then hard-coded cases (stations not found in table)
    # then try case-insensitive matching
    if station in mapping.keys():
        logging.debug(station)
        key = mapping[station]
        params[key]['Station_Name'] = key
        return params[key]
    elif station == 'Herbie Alley':
        params = {}
        params['ID'] = '8697'
        params['Site_Code'] = 'HRB'
        params['Region'] = 'Ross Island Vicinity'
        params['Station_Name'] = 'Herbie Alley'
        params['Lat, Lon'] = '-78.10, 166.68'
        params['Elev'] = '30m'
        return params
    elif station == 'Mizuho II':
        params = {}
        params['ID'] = '21359'
        params['Site_Code'] = 'MI2'
        params['Region'] = 'High Polar Plateau'
        params['Station_Name'] = 'Mizuho II'
        params['Lat, Lon'] = '-70.70, 44.29'
        params['Elev'] = '2260m'
        return params
    elif station not in params.keys():
        logging.debug(station)
        (key,) = [k for k in params.keys() if re.match(station, k, re.I)]
        params[key]['Station_Name'] = key
        return params[key]
    # reduce to station and return parameters
    return params[station]


# PURPOSE: Compute dew point t, virtual t, specific humidity and mixing ratio
# http://cires1.colorado.edu/~voemel/vp.html
# https://www.eol.ucar.edu/projects/ceop/dm/documents/refdata_report/eqns.html
# https://github.com/NCAR/ncl/blob/master/ni/src/lib/nfpfort/mixhum_ptrh.f
# http://glossary.ametsoc.org/wiki/Virtual_temperature
# http://glossary.ametsoc.org/wiki/Mixing_ratio
def derived_variables(T, P, RH):
    """
    Derive additional variables from station observations

    Parameters
    ----------
    T: np.ndarray
        Air temperature
    P: np.ndarray
        Surface pressure
    RH: np.ndarray
        Relative humidity

    Returns
    -------
    Q: np.ndarray
        Specific humidity
    Rv: np.ndarray
        Mixing ratio
    Ev: np.ndarray
        Vapor pressure
    Tv: np.ndarray
        Virtual temperature
    Td: np.ndarray
        Dew point temperature
    """
    # ratio of the molecular weights of water vapor to dry air
    epsilon = 0.622
    # calibration pressure and temperature
    pc = 6.112
    tc = 243.5
    # saturation vapor pressure (mb)
    Es = pc * np.exp((17.67 * T) / (T + tc))
    # vapor pressure *mb)
    Ev = Es * (RH / 100.0)
    # dew point temperature
    Td = np.log(Ev / pc) * tc / (17.67 - np.log(Ev / pc))
    # specific humidity
    Q = 0.001 * (epsilon * Ev) / (P - (0.378 * Ev))
    # mixing ratio
    Rv = epsilon * Ev / (P - Ev)
    # virtual temperature (K)
    VTk = (T + 273.15) * (1.0 + Rv / epsilon) / (1.0 + Rv)
    # virtual temperature (C)
    Tv = VTk - 273.15
    return (Q, Rv, Ev, Tv, Td)


def sea_level_pressure(Z, T, P, Ev, Tv):
    """
    Derive mean sea level pressure using hypsometric equation

    Parameters
    ----------
    Z: float
        Station elevation
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
    MSLP: np.ndarray
        Mean sea level pressure
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
    # use dry-adiabatic lapse rate for most stations
    # use average adiabatic lapse rate for low-level stations
    # set reduction constant for low-level stations
    if Z > 50:
        LRadj = LRdry * Z / 2.0
        Padj = np.copy(P)
    else:
        LRadj = LRave * Z / 2.0
        Padj = P * (1.0 + Z / (Rc * Tv))
    # mean sea level pressure for station
    MSLP = Padj * np.exp((gamma * Z) / (Rd * (Tk + LRadj + Ev * Ch)))
    return MSLP


# PURPOSE: sync local automatic weather station files with server
def amrdc_station_retrieve(
    base_dir,
    YEAR=None,
    MODE=0o775,
):
    # get logger
    logger = logging.getLogger(__name__)
    # directory setup
    base_dir = pathlib.Path(base_dir).expanduser().absolute()
    # get list of stations
    URL = 'https://amrdcdata.ssec.wisc.edu/data-api/aws/list/station_years'
    logger.debug(URL)
    stations = gravtk.utilities.from_json(URL)
    # compile HTML parser for lxml
    parser = lxml.etree.HTMLParser()

    # observations of interest
    variables = dict(
        air_temp='temperature',
        pressure='pressure',
        rh='humidity',
    )
    # derived variables
    derived = [
        'dew_temp',
        'mix_ratio',
        'mslp',
        'sh',
        'vapor_pressure',
        'virtual_temp',
    ]
    # netCDF4 structure
    struct = dict(dimensions=('time', 'station'), variables={})
    struct['variables']['elev'] = ('station',)
    struct['variables']['lat'] = ('station',)
    struct['variables']['lon'] = ('station',)
    for key, var in variables.items():
        struct['variables'][key] = ('station', 'time')
    for var in derived:
        struct['variables'][var] = ('station', 'time')
    # netCDF4 attributes
    attributes = dict(ROOT={})
    attributes['ROOT']['featureType'] = 'timeSeries'
    attributes['ROOT']['source'] = 'surface observation'
    attributes['ROOT']['institution'] = 'UW SSEC'
    # station
    attributes['station'] = {}
    # time (sceonds since unix epoch)
    epoch = '1970-01-01T00:00:00'
    attributes['time'] = {}
    attributes['time']['units'] = f'seconds since {epoch}'
    attributes['time']['long_name'] = 'time'
    attributes['time']['standard_name'] = 'time of measurement'
    attributes['time']['calendar'] = 'standard'
    # elevation
    attributes['elev'] = {}
    attributes['elev']['units'] = 'meters'
    attributes['elev']['long_name'] = 'elevation'
    attributes['elev']['description'] = 'station elevation'
    # latitude and longitude
    attributes['lat'] = {}
    attributes['lat']['units'] = 'degrees_north'
    attributes['lat']['long_name'] = 'latitude'
    attributes['lat']['description'] = 'station latitude'
    attributes['lon'] = {}
    attributes['lon']['units'] = 'degrees_east'
    attributes['lon']['long_name'] = 'longitude'
    attributes['lon']['description'] = 'station longitude'
    # observations
    # air temperature
    attributes['air_temp'] = {}
    attributes['air_temp']['units'] = 'degC'
    attributes['air_temp']['long_name'] = 'air temperature'
    attributes['air_temp']['coordinates'] = 'lat lon'
    # surface pressure
    attributes['pressure'] = {}
    attributes['pressure']['units'] = 'hPa'
    attributes['pressure']['long_name'] = 'air pressure'
    attributes['pressure']['coordinates'] = 'lat lon'
    # relative humidity
    attributes['rh'] = {}
    attributes['rh']['units'] = '%'
    attributes['rh']['long_name'] = 'relative humidity'
    attributes['rh']['coordinates'] = 'lat lon'
    # derived quantities
    # dew point temperature
    attributes['dew_temp'] = {}
    attributes['dew_temp']['units'] = 'degC'
    attributes['dew_temp']['long_name'] = 'dew point temperature'
    attributes['dew_temp']['coordinates'] = 'lat lon'
    # mean sea level pressure
    attributes['mslp'] = {}
    attributes['mslp']['units'] = 'hPa'
    attributes['mslp']['long_name'] = 'mean sea level pressure'
    # mixing ratio
    attributes['mix_ratio'] = {}
    attributes['mix_ratio']['units'] = 'kg kg**-1'
    attributes['mix_ratio']['long_name'] = 'mixing ratio'
    attributes['mix_ratio']['coordinates'] = 'lat lon'
    # specific humidity
    attributes['sh'] = {}
    attributes['sh']['units'] = 'kg kg**-1'
    attributes['sh']['long_name'] = 'specific humidity'
    attributes['sh']['coordinates'] = 'lat lon'
    # vapor pressure
    attributes['vapor_pressure'] = {}
    attributes['vapor_pressure']['units'] = 'hPa'
    attributes['vapor_pressure']['long_name'] = 'vapor pressure'
    attributes['vapor_pressure']['coordinates'] = 'lat lon'
    # virtual temperature
    attributes['virtual_temp'] = {}
    attributes['virtual_temp']['units'] = 'degC'
    attributes['virtual_temp']['long_name'] = 'virtual temperature'
    attributes['virtual_temp']['coordinates'] = 'lat lon'

    # compile numerical expression operator
    rx = re.compile(r'[-+]?(?:(?:\d*\.\d+)|(?:\d+\.?))(?:[Ee][+-]?\d+)?')

    # for each AWS station
    for station, years in stations.items():
        # reduce list of years if applicable
        if YEAR is not None:
            years = sorted(set(years) & set(YEAR))
        # for each year to run
        for i, year in enumerate(years):
            # create directory for year
            directory = base_dir.joinpath(str(year))
            directory.mkdir(parents=True, exist_ok=True, mode=MODE)
            # fetch station parameters for year (or all stations)
            try:
                parameters = fetch_parameters(station, year, parser=parser)
            except (ValueError, KeyError) as exc:
                logger.debug(traceback.format_exc())
                parameters = fetch_parameters(station, 'all', parser=parser)
            # extract parameters
            station_id = rx.findall(parameters.pop('ID'))
            elevation = rx.findall(parameters.pop('Elev'))
            lat, lon = rx.findall(parameters.pop('Lat, Lon'))
            # update attributes for station
            attributes['station'].update(parameters)
            attributes['station']['_Encoding'] = 'ascii'
            # build url for querying JSON data
            url = build_query(station, year, interval='10')
            response = gravtk.utilities.from_json(url)
            nrows = len(response['data'])
            header = response['header']
            # output data dictionary
            output = {}
            output['station'] = np.array(station_id, dtype='|S')
            output['elev'] = np.array(elevation, dtype=np.float64)
            output['lat'] = np.array([lat], dtype=np.float64)
            output['lon'] = np.array([lon], dtype=np.float64)
            # datetimes (will be converted to delta times for output)
            datetime = np.zeros((nrows), dtype='datetime64[s]')
            for key, var in variables.items():
                output[key] = np.ma.zeros((1, nrows), fill_value=444)
            for i, row in enumerate(response['data']):
                # build datetime variable
                date = row[header.index('date')]
                time = row[header.index('time')]
                datetime[i] = f'{date}T{time}:00'
                # get other variables
                for key, var in variables.items():
                    output[key][0, i] = np.float64(row[header.index(var)])
            # find unique times (some stations repeat dates)
            datetime, index = np.unique(datetime, return_index=True)
            # update mask and replace invalid values with nan
            for key, var in variables.items():
                output[key].mask = output[key].data == output[key].fill_value
                output[key] = output[key][:, index].filled(fill_value=np.nan)
            # convert datetimes to delta times
            output['time'] = gravtk.time.convert_datetime(datetime, epoch=epoch)
            # derive additional quantities
            Q, Rv, Ev, Tv, Td = derived_variables(
                output['air_temp'], output['pressure'], output['rh']
            )
            output['mslp'] = sea_level_pressure(
                output['elev'], output['air_temp'], output['pressure'], Ev, Tv
            )
            # save derived quantities to output
            output['dew_temp'] = Td.copy()
            output['mix_ratio'] = Rv.copy()
            output['sh'] = Q.copy()
            output['vapor_pressure'] = Ev.copy()
            output['virtual_temp'] = Tv.copy()
            # output data to netCDF4 file
            name = re.sub(r'\s+', '_', station)
            filename = directory.joinpath(f'AMRDC_AWS_{name}_{year:4d}.nc')
            logger.info(filename)
            # write data to netCDF4 file
            mdlhmc.spatial.to_netCDF4(
                filename, output, attributes, struct, mode='w'
            )
            # change the permissions mode
            filename.chmod(mode=MODE)
            # delete attributes to prevent copying to other station
            attributes['station'] = {}


# PURPOSE: create argument parser
def arguments():
    parser = argparse.ArgumentParser(
        description="""Downloads automatic weather station (AWS) data from the
            Antarctic Meteorological Research and Data Center (AMRDC)
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
    # years to run
    parser.add_argument(
        '--year',
        '-Y',
        type=int,
        nargs='+',
        help='Years to download',
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
    # run download program
    amrdc_station_retrieve(args.directory, YEAR=args.year, MODE=args.mode)


# run main program
if __name__ == '__main__':
    main()
