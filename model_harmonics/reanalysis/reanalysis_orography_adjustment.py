#!/usr/bin/env python
"""
reanalysis_orography_adjustment.py
Written by Tyler Sutterley (10/2026)
Calculate reanalysis pressure fields at new model orographies
    using the model level fields and coefficients (A and B)

Model level coefficients are obtained using equation 3.17 of
    Simmons and Burridge (1981) and the methodology of Trenberth et al (1993)

Reanalysis models:
    ERA-Interim:
        http://apps.ecmwf.int/datasets/data/interim-full-moda
    ERA5:
        http://apps.ecmwf.int/data-catalogues/era5/?class=ea
    MERRA-2:
        https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/
    JRA-3Q:
        https://gdex.ucar.edu/datasets/d640000/
        https://www.data.jma.go.jp/jra/html/JRA-3Q/index_en.html

COMMAND LINE OPTIONS:
    -D X, --directory X: Working data directory
    -Y X, --year X: years to run
    -d x, --dem x: Digital Elevation Model file
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

REFERENCES:
    A. J. Simmons, and D. M. Burridge, "An energy and angular-momentum
        conserving finite-difference scheme and hybrid vertical coordinates."
        Monthly Weather Review., 109, 758-766, (1981).
        https://doi.org/10.1175/1520-0493(1981)109<0758:AEAAMC>2.0.CO;2

    K. E. Trenberth, J. C. Berry, and L. E. Buja, "Vertical interpolation
        and truncation of model-coordinate data."
        NCAR Technical Note NCAR/TN-396+STR, 54 pp., (1993).
        https://doi.org/10.5065/D6HX19NH

UPDATE HISTORY:
    Updated 10/2026: use struct dictionary to define netCDF4 parameters
        add JRA-3Q reanalysis to list of optional models to run
    Updated 05/2023: use pathlib to define and operate on paths
    Updated 03/2023: use full path to output file in verbose logging
    Updated 12/2022: single implicit import of spherical harmonic tools
    Updated 05/2022: use argparse descriptions within sphinx documentation
    Updated 12/2021: can use variable loglevels for verbose output
    Updated 10/2021: using python logging for handling verbose output
    Updated 07/2021: can use input files to define command line arguments
        added check for ERA5 expver dimension (denotes mix of ERA5 and ERA5T)
    Updated 05/2021: define int/float precision to prevent deprecation warning
    Updated 03/2021: automatically update years to run based on current time
    Updated 01/2021: read from netCDF4 file in slices to reduce memory load
    Updated 12/2020: using argparse to set command line options
    Written 01/2020
"""

from __future__ import print_function

import sys
import os
import re
import time
import logging
import netCDF4
import pathlib
import argparse
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


# PURPOSE: calculate reanalysis pressure fields at new model orographies
def reanalysis_orography_adjustment(
    base_dir, MODEL, YEAR=None, DEM=None, MODE=0o775
):
    # get logger
    logger = logging.getLogger(__name__)
    # directory setup
    base_dir = pathlib.Path(base_dir).expanduser().absolute()
    ddir = base_dir.joinpath(MODEL)

    # set model specific parameters
    # use standard weights for equirectangular grids
    WEIGHT = None
    if MODEL in ('ERA-Interim', 'ERA5'):
        # invariant parameters file
        input_invariant_file = f'{MODEL}-Invariant-Parameters.nc'
        # coordinate parameters file
        input_coordinate_file = f'{MODEL}_coordvars.nc'
        # surface pressure file format
        input_pressure_file = f'{MODEL}-Monthly-SP-{{0}}.nc'
        # regular expression pattern for finding files
        regex_pattern = rf'{MODEL}\-Monthly\-Levels\-({{0}})\.nc$'
        # output file format
        output_file_format = f'{MODEL}-Monthly-SP-Levels-{{0}}.nc'
        SURFNAME = 'z'
        ZNAME = 'z'
        VARNAME = 'sp'
        TNAME = 't'
        QNAME = 'q'
        DIFFNAME = 'dp'
        LONNAME = 'longitude'
        LATNAME = 'latitude'
        TIMENAME = 'time' if (MODEL == 'ERA-Interim') else 'valid_time'
        LEVELNAME = 'lvl'
        ANAME, BNAME = ('a_half', 'b_half')
        AINTERFACE, BINTERFACE = ('a_interface', 'b_interface')
        # hours since 1900-01-01 00:00:0.0
        TIME_LONGNAME = 'Time'
        GRAVITY = 9.80665
    elif MODEL == 'MERRA-2':
        # invariant parameters file
        input_invariant_file = 'MERRA2_101.const_2d_asm_Nx.00000000.nc4'
        # coordinate parameters file
        input_coordinate_file = 'MERRA2_101.const_3d_coords_Nx.00000000.nc4'
        # surface pressure file format
        input_pressure_file = 'MERRA2_{0}.tavgM_2d_slv_Nx.{1}{2}.SUB.nc'
        # regular expression pattern for finding files
        regex_pattern = r'MERRA2_(\d+).tavgM_3d_asm_Nv.({0})(\d{{2}}).SUB.nc$'
        # output file format
        output_file_format = 'MERRA2_{0}.tavgM_3d_asm_PS.{1}{2}.SUB.nc'
        SURFNAME = 'PHIS'
        ZNAME = 'PHIS'
        VARNAME = 'PS'
        TNAME = 'T'
        QNAME = 'QV'
        DIFFNAME = 'dP'
        LONNAME = 'lon'
        LATNAME = 'lat'
        TIMENAME = 'time'
        LEVELNAME = 'lev'
        ANAME, BNAME = ('a_half', 'b_half')
        AINTERFACE, BINTERFACE = ('a_interface', 'b_interface')
        # minutes since start of file
        TIME_LONGNAME = 'Time'
        GRAVITY = 9.80665
    elif MODEL == 'JRA-3Q':
        # invariant parameters file
        input_invariant_file = (
            'jra3q.tl479_surf.0_3_4.gp-sfc-cn-gauss.1947090100_1947090100.nc'
        )
        # coordinate parameters file
        input_coordinate_file = 'jra3q.mdl-hyb.coefficients.nc'
        # surface pressure and specific humidity file formats
        input_pressure_file = 'jra3q.anl_surf.pres-sfc-an-gauss.{0}{1}.nc'
        input_humidity_file = 'jra3q.anl_mdl.spfh-hyb-an-gauss-mn.{0}{1}.nc'
        # regular expression pattern for finding files
        regex_pattern = r'jra3q\.anl_mdl\.tmp-hyb-an-gauss-mn\.({0})(\d+).nc$'
        # output file format
        output_file_format = 'jra3q.anl_mdl.pres-sfc-an-gauss.{0}{1}.nc'
        SURFNAME = 'gp-sfc-cn-gauss'
        ZNAME = 'hgt-hyb-an-gauss'
        VARNAME = 'pres-sfc-an-gauss'
        TNAME = 'tmp-hyb-an-gauss-mn'
        QNAME = 'spfh-hyb-an-gauss-mn'
        DIFFNAME = 'dpres-hyb-an-gauss'
        LONNAME = 'lon'
        LATNAME = 'lat'
        TIMENAME = 'time'
        LEVELNAME = 'hybrid_half_level'
        WEIGHT = 'weight'
        ANAME, BNAME = ('a_hybrid_half_level', 'b_hybrid_half_level')
        AINTERFACE, BINTERFACE = ('a_hybrid_level', 'b_hybrid_level')
        # hours since 1900-01-01 00:00:00
        TIME_LONGNAME = 'time'
        GRAVITY = 9.80665

    # dictionary defining output structure
    struct = dict(
        dimensions=(TIMENAME, LATNAME, LONNAME),
        variables={
            VARNAME: (TIMENAME, LATNAME, LONNAME),
            DIFFNAME: (TIMENAME, LATNAME, LONNAME),
            ZNAME: (LATNAME, LONNAME),
            'surface': (LATNAME, LONNAME),
        },
    )

    # dictionary defining file-level and variable attributes
    attributes = dict(ROOT={})
    # reference attribute
    REFERENCE = f'Output from {pathlib.Path(sys.argv[0]).name}'
    attributes['ROOT']['reference'] = REFERENCE
    # variable attributes
    attributes[LONNAME] = dict(
        long_name='Longitude',
        units='degrees_east',
    )
    attributes[LATNAME] = dict(
        long_name='Latitude',
        units='degrees_north',
    )
    attributes[TIMENAME] = dict(
        long_name=TIME_LONGNAME,
        standard_name='time',
        calendar='standard',
    )
    # Defining attributes for output variables
    attributes[VARNAME] = dict(
        long_name='Surface_Pressure',
        units='Pa',
    )
    attributes[DIFFNAME] = dict(
        long_name='Pressure_Differences_from_Model',
        units='Pa',
    )
    attributes[ZNAME] = dict(
        long_name='Surface_Height_from_Model',
        units='m',
    )
    attributes['surface'] = dict(
        long_name='Surface_Height_from_DEM',
        units='m',
    )
    # append additional weight variable for gaussian grid models
    if MODEL in ('JRA-3Q',):
        struct['variables'][WEIGHT] = (LATNAME,)
        attributes[WEIGHT] = dict(
            long_name='gaussian weight', short_name='wgt', units='1'
        )

    # read model orography for dimensions
    geopotential, lon, lat = ncdf_invariant(
        ddir.joinpath(input_invariant_file), LONNAME, LATNAME, SURFNAME
    )
    # calculate meshgrid from latitude and longitude
    gridlon, gridlat = np.meshgrid(lon, lat)
    gridtheta = np.radians(90.0 - gridlat)
    cos2th = np.cos(2.0 * gridtheta)
    # read parameters for calculating pressures at levels
    # flips the order of the levels so that bottom=0
    lev, A, B, AI, BI = ncdf_coordinates(
        ddir.joinpath(input_coordinate_file),
        LEVELNAME,
        ANAME,
        BNAME,
        AINTERFACE,
        BINTERFACE,
    )

    # read digital elevation model for surface elevation
    with netCDF4.Dataset(ddir.joinpath(DEM), 'r') as fileID:
        dem = fileID.variables['surface'][:].copy()
        fv = fileID.variables['surface']._FillValue

    # Gas constant for dry air
    R_dry = 287.06
    # minimum allowable pressure at the top of the atmosphere
    Pmin = 0.1

    # read each reanalysis pressure field for each year
    regex_years = r'\d{4}' if (YEAR is None) else '|'.join(map(str, YEAR))
    rx = re.compile(regex_pattern.format(regex_years), re.VERBOSE)
    input_files = sorted([f for f in ddir.iterdir() if rx.match(f.name)])
    # for each reanalysis file
    for i, temperature_file in enumerate(input_files):
        # read input temperature and specific humidity data
        logger.debug(str(temperature_file))
        fid = [None] * 3
        fid[0] = netCDF4.Dataset(temperature_file, mode='r')
        # extract shape from temperature variable
        ntime, nlevels, nlat, nlon = fid[0].variables[TNAME].shape
        # invalid value
        fill_value = fid[0].variables[TNAME]._FillValue
        # dictionary with output variables and dimensions
        dinput = {}
        # output adjusted surface pressure and differences
        for var in (VARNAME, DIFFNAME):
            dinput[var] = np.ma.zeros((ntime, nlat, nlon), dtype='f')
            dinput[var].set_fill_value(fill_value)
        # copy DEM surface
        dinput['surface'] = dem.copy()
        # convert geopotential to orography (above mean sea level)
        # https://software.ecmwf.int/wiki/x/WAfEB
        GPH = geopotential / GRAVITY
        # orthometric height from List (1958)
        # as described in Boy and Chao (2005)
        dinput[ZNAME] = ((1.0 - 0.002644 * cos2th) * GPH) + (
            (1.0 - 0.0089 * cos2th) * (GPH**2) / 6.245e6
        )
        # extract time and time units
        dinput[TIMENAME] = np.copy(fid[0].variables[TIMENAME][:])
        attributes[TIMENAME]['units'] = fid[0].variables[TIMENAME].units
        # copy latitude and longitude
        dinput[LONNAME] = lon.copy()
        dinput[LATNAME] = lat.copy()

        if MODEL in ('MERRA-2'):
            # extract date from temperature files
            MOD, YEAR, MONTH = rx.findall(temperature_file.name).pop()
            # output monthly filename
            FILENAME = output_file_format.format(MOD, YEAR, MONTH)
            output_file = ddir.joinpath(FILENAME)
            # specific humidity from same file as temperature
            fid[1] = fid[0]
            # read input surface pressure data
            pressure_file = ddir.joinpath(
                input_pressure_file.format(MOD, YEAR, MONTH)
            )
            logger.debug(str(pressure_file))
            with netCDF4.Dataset(pressure_file, 'r') as fid[2]:
                pressure = fid[2].variables[VARNAME][:]
        elif MODEL in ('ERA-Interim', 'ERA5'):
            # extract year from temperature files
            (YEAR,) = rx.findall(temperature_file.name)
            # output yearly filename
            FILENAME = output_file_format.format(YEAR)
            output_file = ddir.joinpath(FILENAME)
            # specific humidity from same file as temperature
            fid[1] = fid[0]
            # read input surface pressure data
            pressure_file = ddir.joinpath(input_pressure_file.format(YEAR))
            logger.debug(str(pressure_file))
            with netCDF4.Dataset(pressure_file, 'r') as fid[2]:
                pressure = np.copy(fid[2].variables[VARNAME][:])
        elif MODEL in ('JRA-3Q'):
            # extract date from temperature files
            YEAR, MONTH = rx.findall(temperature_file.name).pop()
            # output monthly filename
            FILENAME = output_file_format.format(YEAR, MONTH)
            output_file = ddir.joinpath(FILENAME)
            # extract the A and B coefficients for the hybrid levels
            A = fid[0].variables[ANAME][:]
            B = fid[0].variables[BNAME][:]
            AI = fid[0].variables[AINTERFACE][:]
            BI = fid[0].variables[BINTERFACE][:]
            # extract the gaussian grid variables
            dinput[WEIGHT] = fid[0].variables[WEIGHT][:]
            # specific humidity data file
            humidity_file = ddir.joinpath(
                input_humidity_file.format(YEAR, MONTH)
            )
            logger.debug(str(humidity_file))
            fid[1] = netCDF4.Dataset(humidity_file, 'r')
            # read input surface pressure data
            pressure_file = ddir.joinpath(
                input_pressure_file.format(YEAR, MONTH)
            )
            logger.debug(str(pressure_file))
            with netCDF4.Dataset(pressure_file, 'r') as fid[2]:
                # reorder dimensions to match the required order
                dims = fid[2].variables[VARNAME].dimensions
                order = [dims.index(d) for d in (TIMENAME, LATNAME, LONNAME)]
                pressure = fid[2].variables[VARNAME][:].transpose(order)

        # iterate over dates
        for t in range(ntime):
            # extract temperature and specific humidity for time t
            if fid[0].variables[TNAME].ndim == 5:
                # check dimensions for expver slice
                t_time, expver = ncdf_expver(fid[0], t, TNAME)
                q_time, _ = ncdf_expver(fid[1], t, QNAME, index=expver)
            else:
                # temperature and specific humidity
                # reverse layers so bottom=0
                t_time = np.flipud(fid[0].variables[TNAME][t, :, :, :])
                q_time = np.flipud(fid[1].variables[QNAME][t, :, :, :])
            # convert to masked arrays
            t_time = np.ma.masked_equal(t_time, fill_value)
            q_time = np.ma.masked_equal(q_time, fill_value)
            # calculate geopotential over model levels
            geopotential_height = np.empty((nlat, nlon), dtype=np.float32)
            # start with surface geopotential (m^2/s^2)
            geopotential_height[:, :] = geopotential.copy()
            # convert geopotential to orography (above mean sea level)
            # https://software.ecmwf.int/wiki/x/WAfEB
            GPH = geopotential_height / GRAVITY
            # orthometric height from List (1958)
            # as described in Boy and Chao (2005)
            orthometric = ((1.0 - 0.002644 * cos2th) * GPH) + (
                (1.0 - 0.0089 * cos2th) * (GPH**2) / 6.245e6
            )
            # extract surface pressure for time t
            p_time = pressure[t, :, :]
            # start with original surface pressure values for time
            dinput[VARNAME][t, :, :] = p_time.copy()

            # find valid elevations below orthometric height
            inlevel = (dem != fv) & (dem > 0) & (dem < orthometric)
            if np.any(inlevel):
                # estimate expected pressure
                indy, indx = np.nonzero(inlevel)
                Pexp = expected_pressure(
                    dem[indy, indx],
                    orthometric[indy, indx],
                    t_time[0, indy, indx],
                    p_time[indy, indx],
                    q_time[0, indy, indx],
                )
                dinput[VARNAME].data[t, indy, indx] = Pexp
            # copy orthometric height for iteration
            previous = orthometric.copy()

            # for each of the reanalysis model layers
            for k in range(nlevels):
                # check if all dem values are below previous orthometric
                if np.all(dem < previous):
                    break
                # specific humidity and temperature for level k and time t
                T = t_time[k, :, :]
                QV = q_time[k, :, :]
                # calculate virtual temperature
                Tv = (1.0 + 0.609133 * QV) * T
                # calculate numerator and denominator for pressure ratio
                Pnum = AI[k] + BI[k] * p_time
                # check if there is an upper bound
                if (k + 1) == len(AI):
                    # use minimum pressure for top-of-atmosphere
                    Pdom = Pmin
                else:
                    # add a threshold to avoid dividing by zero
                    Pdom = np.maximum(AI[k + 1] + BI[k + 1] * p_time, Pmin)
                # calculate geopotential difference using hypsometric equation
                # add level to geopotential_levels
                geopotential_height[:, :] += R_dry * Tv * np.log(Pnum / Pdom)
                # convert geopotential to orography (above mean sea level)
                # https://software.ecmwf.int/wiki/x/WAfEB
                GPH = geopotential_height / GRAVITY
                # orthometric height at the upper interface
                orthometric = ((1.0 - 0.002644 * cos2th) * GPH) + (
                    (1.0 - 0.0089 * cos2th) * (GPH**2) / 6.245e6
                )
                # find if any heights within level
                inlevel = (dem != fv) & (dem >= previous) & (dem < orthometric)
                if np.any(inlevel):
                    indy, indx = np.nonzero(inlevel)
                    dz = dem[indy, indx] - previous[indy, indx]
                    dh = orthometric[indy, indx] - previous[indy, indx]
                    # linearly interpolate level values
                    Aexp = AI[k] + (AI[k + 1] - AI[k]) * (dz / dh)
                    Bexp = BI[k] + (BI[k + 1] - BI[k]) * (dz / dh)
                    # calculate expected pressure
                    Pexp = Aexp + Bexp * p_time[indy, indx]
                    dinput[VARNAME].data[t, indy, indx] = Pexp
                # update orthometric height for iteration
                previous = orthometric.copy()
        # replace invalid values with fill_value
        dinput[VARNAME].mask = (
            dinput[VARNAME].data == dinput[VARNAME].fill_value
        )
        dinput[VARNAME].data[dinput[VARNAME].mask] = dinput[VARNAME].fill_value
        # calculate pressure differences from original
        dinput[DIFFNAME] = dinput[VARNAME] - pressure
        dinput[DIFFNAME].mask |= np.isclose(dinput[VARNAME], pressure)
        dinput[VARNAME].data[dinput[VARNAME].mask] = dinput[VARNAME].fill_value
        # write structured data to netCDF4 file
        mdlhmc.spatial.to_netCDF4(output_file, dinput, attributes, struct)
        # set the permissions level of the output file to MODE
        output_file.chmod(mode=MODE)
        # clear dinput dictionary variable
        dinput = None
        # close the input netCDF4 files
        ncdf_close_all(fid)


# PURPOSE: read reanalysis invariant parameters (geopotential,lat,lon)
def ncdf_invariant(FILENAME, LONNAME, LATNAME, ZNAME):
    # get logger
    logger = logging.getLogger(__name__)
    logger.debug(str(FILENAME))
    with netCDF4.Dataset(FILENAME, mode='r') as fileID:
        geopotential = fileID.variables[ZNAME][:].squeeze()
        longitude = fileID.variables[LONNAME][:].copy()
        latitude = fileID.variables[LATNAME][:].copy()
    return (geopotential, longitude, latitude)


# PURPOSE: Compute expected pressure
# http://cires1.colorado.edu/~voemel/vp.html
# https://www.eol.ucar.edu/projects/ceop/dm/documents/refdata_report/eqns.html
# https://github.com/NCAR/ncl/blob/master/ni/src/lib/nfpfort/mixhum_ptrh.f
# http://glossary.ametsoc.org/wiki/Virtual_temperature
# http://glossary.ametsoc.org/wiki/Mixing_ratio
def expected_pressure(Z, H, T, P, RH):
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
    RH: np.ndarray
        Relative humidity

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
    # ratio of the molecular weights of water vapor to dry air
    epsilon = 0.622
    # calibration pressure and temperature
    pc = 6.112
    tc = 243.5
    # pressure converted to millibars
    mbar = P / 100.0
    # temperature change relative to a change in pressure
    # 0.12 K/hPa
    Ch = 0.12
    # characteristic gas constant of dry air
    Rc = 29.27
    # temperature in kelvin
    Tk = T + 273.15
    # saturation vapor pressure (mb)
    Es = pc * np.exp((17.67 * T) / (T + tc))
    # vapor pressure *mb)
    Ev = Es * (RH / 100.0)
    # mixing ratio
    Rv = epsilon * Ev / (mbar - Ev)
    # virtual temperature (K)
    VTk = (T + 273.15) * (1.0 + Rv / epsilon) / (1.0 + Rv)
    # virtual temperature (C)
    Tv = VTk - 273.15
    # height change from model orthometric height to DEM
    dZ = H - Z
    # use dry-adiabatic lapse rate for most stations
    # use average adiabatic lapse rate for low-level stations
    # set reduction constant for low-level stations
    LRadj = np.where(H > 50, LRdry * dZ / 2.0, LRave * dZ / 2.0)
    Padj = np.where(H > 50, mbar, mbar * (1.0 + dZ / (Rc * Tv)))
    # expected pressure for station at model orthometric height
    Pexp = Padj * np.exp((gamma * dZ) / (Rd * (Tk + LRadj + Ev * Ch)))
    return Pexp * 100.0


# PURPOSE: extract temperature and specific humidity variables
# from a 5d netCDF4 dataset
# ERA5 expver dimension (denotes mix of ERA5 and ERA5T)
def ncdf_expver(fileID, slice, VARNAME, index=None):
    ntime, nexp, nlevel, nlat, nlon = fileID.variables[VARNAME].shape
    # if expver is specified, check if data is valid for expver
    if index is not None and np.any(fileID.variables[VARNAME][slice, index, :]):
        # reverse layers so bottom=0
        variable = np.flipud(fileID.variables[VARNAME][slice, index, :])
        # return the reduced variables
        return variable, index
    # reduced variable (temperature or specific humidity) for time
    variable = np.zeros((nlevel, nlat, nlon))
    # iterate over expver slices to find valid outputs
    for j in range(nexp):
        # check if any are valid for expver
        if np.any(fileID.variables[VARNAME][slice, j, :]):
            # reverse layers so bottom=0
            variable = np.flipud(fileID.variables[VARNAME][slice, j, :])
            index = j
            break
    # return the reduced variables and the valid expver slice
    return variable, index


# PURPOSE: read reanalysis invariant parameters (geopotential,lat,lon)
def ncdf_invariant(FILENAME, LONNAME, LATNAME, ZNAME):
    # get logger
    logger = logging.getLogger(__name__)
    logger.debug(str(FILENAME))
    with netCDF4.Dataset(FILENAME, mode='r') as fileID:
        geopotential = fileID.variables[ZNAME][:].squeeze()
        longitude = fileID.variables[LONNAME][:].copy()
        latitude = fileID.variables[LATNAME][:].copy()
    return (geopotential, longitude, latitude)


# PURPOSE: read reanalysis coordinate parameters
# reverse order to go from surface to top-of-atmosphere
def ncdf_coordinates(FILENAME, LEVELNAME, ANAME, BNAME, AINTERFACE, BINTERFACE):
    # get logger
    logger = logging.getLogger(__name__)
    logger.debug(str(FILENAME))
    with netCDF4.Dataset(FILENAME, mode='r') as fileID:
        # reverse layers so bottom=0
        levels = np.flip(fileID.variables[LEVELNAME][:])
        A = np.flip(fileID.variables[ANAME][:])
        B = np.flip(fileID.variables[BNAME][:])
        AI = np.flip(fileID.variables[AINTERFACE][:])
        BI = np.flip(fileID.variables[BINTERFACE][:])
    return (levels, A, B, AI, BI)


# PURPOSE: attempt to close all open netCDF4 files
def ncdf_close_all(fileID: list[__loader__]):
    [fid.close() for fid in fileID if fid is not None and fid._isopen]


# PURPOSE: create argument parser
def arguments():
    parser = argparse.ArgumentParser(
        description="""Calculate reanalysis pressure fields at
            new model orographies
            """,
        fromfile_prefix_chars='@',
    )
    parser.convert_arg_line_to_args = gravtk.utilities.convert_arg_line_to_args
    # command line parameters
    choices = ['ERA-Interim', 'ERA5', 'JRA-3Q', 'MERRA-2']
    parser.add_argument(
        'model',
        type=str,
        nargs='+',
        metavar='MODEL',
        default=['ERA5', 'MERRA-2'],
        choices=choices,
        help='Reanalysis Model',
    )
    # working data directory
    parser.add_argument(
        '--directory',
        '-D',
        type=pathlib.Path,
        default=pathlib.Path.cwd(),
        help='Working data directory',
    )
    # years to run
    now = time.gmtime()
    parser.add_argument(
        '--year',
        '-Y',
        type=int,
        nargs='+',
        default=range(2000, now.tm_year + 1),
        help='Years of model outputs to run',
    )
    # digital elevation model for adjustments
    parser.add_argument(
        '--dem',
        '-d',
        type=str,
        required=True,
        help='Digital elevation model',
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

    # for each reanalysis model
    for MODEL in args.model:
        # run program
        reanalysis_orography_adjustment(
            args.directory,
            MODEL,
            YEAR=args.year,
            DEM=args.dem,
            MODE=args.mode,
        )


# run main program
if __name__ == '__main__':
    main()
