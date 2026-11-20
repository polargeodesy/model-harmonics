#!/usr/bin/env python
"""
reanalysis_pressure_harmonics.py
Written by Tyler Sutterley (07/2026)
Reads atmospheric surface pressure fields from reanalysis and calculates sets of
    spherical harmonics using a thin-layer 2D geometry with realistic earth

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
    -D X, --directory X: Working data directory
    -Y X, --year X: Years of model outputs to run
    --mean X: start and end year for mean
    --redistribute: uniformly redistribute pressure over oceanic values
    -l X, --lmax=X: maximum spherical harmonic degree
    -m X, --mmax=X: maximum spherical harmonic order
    -n X, --love X: Treatment of the Love Love numbers
        0: Han and Wahr (1995) values from PREM
        1: Gegout (2005) values from PREM
        2: Wang et al. (2012) values from PREM
        3: Wang et al. (2012) values from PREM with hard sediment
        4: Wang et al. (2012) values from PREM with soft sediment
    --reference X: Reference frame for load love numbers
        CF: Center of Surface Figure (default)
        CM: Center of Mass of Earth System
        CE: Center of Mass of Solid Earth
    -F X, --format X: output data format
        ascii
        netCDF4
        HDF5
    -V, --verbose: Output information for each output file
    -M X, --mode X: Permission mode of directories and files

PYTHON DEPENDENCIES:
    numpy: Scientific Computing Tools For Python
        https://numpy.org
        https://numpy.org/doc/stable/user/numpy-for-matlab-users.html
    dateutil: powerful extensions to datetime
        https://dateutil.readthedocs.io/en/stable/
    netCDF4: Python interface to the netCDF C library
        https://unidata.github.io/netcdf4-python/netCDF4/index.html
    h5py: Pythonic interface to the HDF5 binary data format.
        https://www.h5py.org/

PROGRAM DEPENDENCIES:
    associated_legendre.py: computes fully-normalized associated Legendre polynomials
    read_love_numbers.py: reads Load Love Numbers from Han and Wahr (1995)
    datum.py: calculate reference parameters for common ellipsoids
    norm_gravity.py: calculates the normal gravity for locations on an ellipsoid
    gen_pressure_stokes.py: converts a pressure field into spherical harmonics
    harmonics.py: spherical harmonic data class for processing GRACE/GRACE-FO
    destripe_harmonics.py: calculates the decorrelation (destriping) filter
        and filters the GRACE/GRACE-FO coefficients for striping errors
    time.py: utilities for calculating time operations
    utilities.py: download and management utilities for files

REFERENCES:
    JP Boy and B Chao, "Precise evaluation of atmospheric loading effects on
        Earth's time-variable gravity field", Journal of Geophysical Research:
        Solid Earth, 110(B8), (2005).
        https://doi.org/10.1029/2002JB002333

    S Swenson and J Wahr, "Estimated effects of the vertical structure of
        atmospheric mass on the time-variable geoid", Journal of Geophysical
        Research: Solid Earth, 107(B9), (2002).
        https://doi.org/10.1029/2000JB000024

UPDATE HISTORY:
    Updated 07/2026: added JRA-3Q reanalysis to list of models
        use authalic area for the grid cell areas
        interpolate EGM2008 from full resolution to reanalysis grid
        changed variable names for JRA-55 and NCEP-CFSR reanalysis
    Updated 05/2023: use pathlib to define and operate on paths
    Updated 03/2023: add root attributes to output netCDF4 and HDF5 files
    Updated 02/2023: use love numbers class with additional attributes
    Updated 12/2022: single implicit import of spherical harmonic tools
        use constants class in place of geoid-toolkit ref_ellipsoid
    Updated 11/2022: use f-strings for formatting verbose or ascii output
    Updated 05/2022: use argparse descriptions within sphinx documentation
    Updated 04/2022: use wrapper function for reading load Love numbers
    Updated 12/2021: can use variable loglevels for verbose output
    Updated 10/2021: using python logging for handling verbose output
        use output harmonic file wrapper routine to write to file
    Updated 09/2021: use GRACE/GRACE-FO month to calendar month converters
    Updated 07/2021: can use input files to define command line arguments
        added check for ERA5 expver dimension (denotes mix of ERA5 and ERA5T)
    Updated 05/2021: define int/float precision to prevent deprecation warning
    Updated 03/2021: automatically update years to run based on current time
    Updated 02/2021: separate inputs to gen_pressure_stokes
    Updated 01/2021: outputs from gen_pressure_stokes are now harmonics objects
    Updated 12/2020: using argparse to set command line options
        using time module for operations and for extracting time units
    Updated 05/2020: use harmonics class for spherical harmonic operations
    Updated 04/2020: set path to load love numbers file
    Updated 01/2020: iterate over dates to calculate for incomplete files
    Updated 10/2019: changing Y/N flags to True/False
    Updated 09/2019: modified regular expression pattern for MERRA-2
    Updated 08/2019: added parameters for NCEP-CFSR, time scale for MERRA-2
    Updated 07/2018: added parameters for ERA5.  added find_new_files function
    Updated 05/2018: added uniform redistribution of oceanic values
    Updated 03/2018: added portions to run different reanalysis model outputs
        simplified love number extrapolation if LMAX is greater than 696
        create an index file for use in least squares mascon program
    Written 03/2018
"""

from __future__ import print_function

import sys
import os
import re
import logging
import netCDF4
import pathlib
import argparse
import datetime
import traceback
import numpy as np
import gravity_toolkit as gravtk
import model_harmonics as mdlhmc
import geoid_toolkit as geoidtk


# PURPOSE: keep track of threads
def info(args):
    logger = logging.getLogger(__name__)
    logger.info(pathlib.Path(sys.argv[0]).name)
    logger.info(args)
    logger.info(f'module name: {__name__}')
    if hasattr(os, 'getppid'):
        logger.info(f'parent process: {os.getppid():d}')
    logger.info(f'process id: {os.getpid():d}')


# PURPOSE: read atmospheric surface pressure fields and convert to harmonics
def reanalysis_pressure_harmonics(
    base_dir,
    MODEL,
    YEARS,
    RANGE=None,
    REDISTRIBUTE=False,
    LMAX=0,
    MMAX=None,
    LOVE_NUMBERS=0,
    REFERENCE=None,
    DATAFORM=None,
    MODE=0o775,
):
    # get logger
    logger = logging.getLogger(__name__)
    # directory setup
    base_dir = pathlib.Path(base_dir).expanduser().absolute()
    ddir = base_dir.joinpath(MODEL)

    # set model specific parameters
    # use standard weights for equirectangular grids
    WEIGHT = None
    if MODEL == 'ERA-Interim':
        # mean file from calculate_mean_pressure.py
        input_mean_file = 'ERA-Interim-Mean-SP-{0:4d}-{1:4d}.nc'
        # invariant parameters file
        input_invariant_file = 'ERA-Interim-Invariant-Parameters.nc'
        # input land-sea mask for ocean redistribution
        input_mask_file = 'ERA-Interim-Invariant-Parameters.nc'
        # regular expression pattern for finding files
        regex_pattern = r'ERA\-Interim\-Monthly\-SP\-({0})\.nc$'
        VARNAME = 'sp'
        ZNAME = 'z'
        LONNAME = 'longitude'
        LATNAME = 'latitude'
        TIMENAME = 'time'
        ELLIPSOID = 'WGS84'
        # land-sea mask variable name and value of oceanic points
        MASKNAME = 'lsm'
        OCEAN = 0
        GRAVITY = 9.80665
    elif MODEL == 'ERA5':
        # mean file from calculate_mean_pressure.py
        input_mean_file = 'ERA5-Mean-SP-{0:4d}-{1:4d}.nc'
        # invariant parameters file
        input_invariant_file = 'ERA5-Invariant-Parameters.nc'
        # input land-sea mask for ocean redistribution
        input_mask_file = 'ERA5-Invariant-Parameters.nc'
        # regular expression pattern for finding files
        regex_pattern = r'ERA5\-Monthly\-SP\-({0})\.nc$'
        VARNAME = 'sp'
        ZNAME = 'z'
        LONNAME = 'longitude'
        LATNAME = 'latitude'
        TIMENAME = 'valid_time'
        ELLIPSOID = 'WGS84'
        # land-sea mask variable name and value of oceanic points
        MASKNAME = 'lsm'
        OCEAN = 0
        GRAVITY = 9.80665
    elif MODEL == 'MERRA-2':
        # mean file from calculate_mean_pressure.py
        input_mean_file = 'MERRA2.Mean_PS.{0:4d}-{1:4d}.nc'
        # invariant parameters file
        input_invariant_file = 'MERRA2_101.const_2d_asm_Nx.00000000.nc4'
        # input land-sea mask for ocean redistribution
        input_mask_file = 'MERRA2_101.const_2d_asm_Nx.00000000.nc4'
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
        # land-sea mask variable name and value of oceanic points
        MASKNAME = 'FROCEAN'
        OCEAN = 1
        GRAVITY = 9.80665
    elif MODEL == 'NCEP-DOE-2':
        # mean file from calculate_mean_pressure.py
        input_mean_file = 'pres.sfc.mean.{0:4d}-{1:4d}.nc'
        # invariant parameters file
        input_invariant_file = 'hgt.sfc.nc'
        # input land-sea mask for ocean redistribution
        input_mask_file = 'land.nc'
        # regular expression pattern for finding files
        regex_pattern = r'pres.sfc.mon.mean.({0}).nc$'
        VARNAME = 'pres'
        ZNAME = 'hgt'
        LONNAME = 'lon'
        LATNAME = 'lat'
        TIMENAME = 'time'
        ELLIPSOID = 'WGS84'
        # land-sea mask variable name and value of oceanic points
        MASKNAME = 'land'
        OCEAN = 0
        # NCEP-DOE-2 reanalysis geopotential heights are already in meters
        GRAVITY = 1.0
    elif MODEL == 'NCEP-CFSR':
        # mean file from calculate_mean_pressure.py
        input_mean_file = 'splanl.mean.gdas.{0:4d}-{1:4d}.nc'
        # invariant parameters file
        input_invariant_file = 'hgt.gdas.nc'
        # input land-sea mask for ocean redistribution
        input_mask_file = 'land.gdas.nc'
        # regular expression pattern for finding files
        regex_pattern = r'splanl.gdas.({0})(\d+).nc$'
        VARNAME = 'ave_sp'
        ZNAME = 'orog'
        LONNAME = 'lon'
        LATNAME = 'lat'
        TIMENAME = 'time'
        ELLIPSOID = 'WGS84'
        # land-sea mask variable name and value of oceanic points
        MASKNAME = 'lsm'
        OCEAN = 0
        # NCEP-CFSR reanalysis geopotential heights are already in meters
        GRAVITY = 1.0
    elif MODEL == 'JRA-55':
        # mean file from calculate_mean_pressure.py
        input_mean_file = 'anl_surf.001_pres.mean.{0:4d}-{1:4d}.nc'
        # invariant parameters file
        input_invariant_file = 'll125.006_gp.2000.nc'
        # input land-sea mask for ocean redistribution
        input_mask_file = 'll125.081_land.2000.nc'
        # regular expression pattern for finding files
        regex_pattern = r'anl_surf125\.001_pres\.({0})(\d+).nc$'
        VARNAME = 'sp'
        ZNAME = 'z'
        LONNAME = 'lon'
        LATNAME = 'lat'
        TIMENAME = 'time'
        ELLIPSOID = 'WGS84'
        # land-sea mask variable name and value of oceanic points
        MASKNAME = 'lsm'
        OCEAN = 0
        GRAVITY = 9.80665
    elif MODEL == 'JRA-3Q':
        # mean file from calculate_mean_pressure.py
        input_mean_file = 'jra3q.mean.pres-sfc-an-gauss.{0:4d}-{1:4d}.nc'
        # invariant parameters file
        input_invariant_file = (
            'jra3q.tl479_surf.0_3_4.gp-sfc-cn-gauss.1947090100_1947090100.nc'
        )
        # input land-sea mask for ocean redistribution
        input_mask_file = (
            'jra3q.tl479_land.2_0_0.land-sfc-cn-gauss.1947090100_1947090100.nc'
        )
        # regular expression pattern for finding files
        regex_pattern = r'jra3q\.anl_surf\.pres-sfc-an-gauss\.({0})(\d+).nc$'
        VARNAME = 'pres-sfc-an-gauss'
        ZNAME = 'gp-sfc-cn-gauss'
        LONNAME = 'lon'
        LATNAME = 'lat'
        TIMENAME = 'time'
        ELLIPSOID = 'WGS84'
        # weight variable name
        WEIGHT = 'weight'
        # land-sea mask variable name and value of oceanic points
        MASKNAME = 'land-sfc-cn-gauss'
        OCEAN = 0
        GRAVITY = 9.80665

    # upper bound of spherical harmonic orders (default = LMAX)
    MMAX = np.copy(LMAX) if not MMAX else MMAX
    # output string for both LMAX == MMAX and LMAX != MMAX cases
    order_str = 'M{MMAX:d}' if (MMAX != LMAX) else ''
    # if redistributing oceanic values to a mean value
    ocean_str = '_OCN' if REDISTRIBUTE else ''
    # output suffix for data formats
    suffix = dict(ascii='txt', netCDF4='nc', HDF5='H5')
    # output subdirectory
    args = (MODEL.upper(), LMAX, order_str, ocean_str)
    output_dir = ddir.joinpath('{0}_PRESSURE_CLM_L{1:d}{2}{3}'.format(*args))
    output_dir.mkdir(mode=MODE, parents=True, exist_ok=True)
    # attributes for output files
    attributes = {}
    attributes['project'] = MODEL
    attributes['product_type'] = 'gravity_field'
    attributes['reference'] = f'Output from {pathlib.Path(sys.argv[0]).name}'

    # read mean pressure field from calculate_mean_pressure.py
    mean_file = ddir.joinpath(input_mean_file.format(RANGE[0], RANGE[1]))
    mean_pressure, lon, lat = ncdf_mean_pressure(
        mean_file, VARNAME, LONNAME, LATNAME
    )
    nlat, nlon = np.shape(mean_pressure)
    # required order of dimensions
    dimensions = [TIMENAME, LATNAME, LONNAME]
    # calculate colatitude
    theta = np.radians(90.0 - lat)
    # calculate meshgrid from latitude and longitude
    gridlon, gridlat = np.meshgrid(lon, lat)
    gridphi = np.radians(gridlon)
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
    # read load love numbers
    LOVE = gravtk.load_love_numbers(
        LMAX,
        LOVE_NUMBERS=LOVE_NUMBERS,
        REFERENCE=REFERENCE,
        FORMAT='class',
    )
    # add attributes for earth parameters
    attributes['earth_model'] = LOVE.model
    attributes['earth_love_numbers'] = LOVE.citation
    attributes['reference_frame'] = LOVE.reference
    # add attributes for maximum degree and order
    attributes['max_degree'] = LMAX
    attributes['max_order'] = MMAX

    # calculate Legendre polynomials
    PLM, dPLM = gravtk.plm_holmes(LMAX, np.cos(theta))
    # interpolate geoid heights
    geoid = geoidtk.interpolate.geoid_height(
        lon, lat, model='EGM2008', tide_system='mean_tide'
    )

    # get reference parameters for ellipsoid
    ellipsoid_params = mdlhmc.datum(ellipsoid=ELLIPSOID)
    # semimajor and semiminor axes of the ellipsoid [m]
    a_axis = ellipsoid_params.a_axis
    b_axis = ellipsoid_params.b_axis
    # ellipsoidal flattening
    flat = ellipsoid_params.flat
    # first numerical eccentricity
    ecc1 = ellipsoid_params.ecc1
    e12 = ecc1**2.0
    # convert from geodetic latitude to geocentric latitude
    # radius of curvature in prime vertical direction (east-west)
    N = a_axis / np.sqrt(1.0 - e12 * np.cos(gridtheta) ** 2.0)
    # radius of curvature in meridional direction (north-south)
    M = a_axis * (1.0 - e12) / (1.0 - e12 * np.cos(gridtheta) ** 2) ** 1.5
    # calculate heights
    height = geoid + orthometric
    # calculate X, Y and Z from geodetic latitude and longitude
    X = (N + height) * np.sin(gridtheta) * np.cos(gridphi)
    Y = (N + height) * np.sin(gridtheta) * np.sin(gridphi)
    Z = (N * (1.0 - ecc1**2.0) + height) * np.cos(gridtheta)
    R = np.sqrt(X**2.0 + Y**2.0 + Z**2.0)
    # calculate normal gravity at latitudes and heights above ellipsoid
    gamma_h, dgamma_dh = geoidtk.norm_gravity(gridlat, height, ELLIPSOID)

    # step size in radians
    dphi = np.radians(np.abs(lon[1] - lon[0]))
    dth = np.radians(np.abs(lat[1] - lat[0]))

    # get indices of land-sea mask if redistributing oceanic points
    if REDISTRIBUTE:
        ii, jj = ncdf_landmask(ddir.joinpath(input_mask_file), MASKNAME, OCEAN)

    # read each reanalysis pressure field and convert to spherical harmonics
    regex_years = r'\d{4}' if (YEARS is None) else '|'.join(map(str, YEARS))
    rx = re.compile(regex_pattern.format(regex_years), re.VERBOSE)
    input_list = sorted([f for f in ddir.iterdir() if rx.match(f.name)])
    # open output date and index files
    output_date_file = output_dir.joinpath(f'{MODEL.upper()}_DATES.txt')
    fid1 = output_date_file.open(mode='w', encoding='utf8')
    output_index_file = output_dir.joinpath(f'{MODEL}_index.txt')
    fid2 = output_index_file.open(mode='w', encoding='utf8')
    # date file header information
    print('{0:8} {1:10}'.format('Month', 'Date'), file=fid1)
    # output file format for spherical harmonic data
    output_file_format = '{0}_CLM_L{1:d}{2}_{3:03d}.{4}'

    # list of output files
    output_list = []
    # for each reanalysis file
    for i, input_file in enumerate(input_list):
        # read input data
        logger.debug(str(input_file))
        with netCDF4.Dataset(input_file, mode='r') as fileID:
            # check dimensions for expver slice
            if fileID.variables[VARNAME].ndim == 4:
                pressure = ncdf_expver(fileID, VARNAME)
            else:
                pressure = fileID.variables[VARNAME][:].copy()
            # update mask variable
            fill_value = fileID.variables[VARNAME]._FillValue
            pressure = np.ma.masked_equal(pressure, fill_value)
            # reorder dimensions to match the required order
            dims = fileID.variables[VARNAME].dimensions
            order = [dims.index(d) for d in dimensions]
            pressure = pressure.transpose(order)
            # read weights for non-uniform (e.g. gaussian) grids
            # or use standard weights for uniform grids
            if WEIGHT is not None:
                weight = dphi * fileID.variables[WEIGHT][:].copy()
            else:
                weight = np.sin(theta) * dphi * dth
            # convert time to Modified Julian Days
            delta_time = np.copy(fileID.variables[TIMENAME][:])
            date_string = fileID.variables[TIMENAME].units
            epoch, to_secs = gravtk.time.parse_date_string(date_string)
            MJD = gravtk.time.convert_delta_time(
                delta_time * to_secs,
                epoch1=epoch,
                epoch2=(1858, 11, 17, 0, 0, 0),
                scale=1.0 / 86400.0,
            )
        # attributes for input files
        attributes['lineage'] = []
        attributes['lineage'].append(input_invariant_file)
        attributes['lineage'].append(input_file.name)

        # iterate over Julian days
        for t, JD in enumerate(MJD + 2400000.5):
            # calculate pressure anomaly for month
            P = pressure[t, :, :] - mean_pressure[:, :]
            # if redistributing oceanic pressure values
            if REDISTRIBUTE and WEIGHT:
                # calculate area of each grid cell
                W = np.kron(np.ones((1, nlon)), weight[:, np.newaxis])
                AREA = M * N * W
                # calculate total area of oceanic points
                TOTAL_AREA = np.sum(AREA[ii, jj])
                # evenly redistribute pressure over oceanic points
                P[ii, jj] = np.sum(P[ii, jj] * AREA[ii, jj]) / TOTAL_AREA
            elif REDISTRIBUTE:
                # calculate area of each grid cell
                AREA = (M * dth) * (N * np.sin(gridtheta) * dphi)
                # calculate total area of oceanic points
                TOTAL_AREA = np.sum(AREA[ii, jj])
                # evenly redistribute pressure over oceanic points
                P[ii, jj] = np.sum(P[ii, jj] * AREA[ii, jj]) / TOTAL_AREA
            # calculate spherical harmonics from pressure/gravity ratio
            Ylms = mdlhmc.gen_pressure_stokes(
                P,
                gamma_h,
                R,
                lon,
                lat,
                LMAX=LMAX,
                MMAX=MMAX,
                WEIGHT=weight,
                PLM=PLM,
                LOVE=LOVE,
            )
            # convert julian dates to calendar then to year-decimal
            YY, MM, DD, hh, mm, ss = gravtk.time.convert_julian(
                JD, FORMAT='tuple'
            )
            (Ylms.time,) = gravtk.time.convert_calendar_decimal(
                YY, MM, day=DD, hour=hh, minute=mm, second=ss
            )
            # calculate GRACE month from calendar dates
            Ylms.month = gravtk.time.calendar_to_grace(YY, MM)
            # add attributes to output harmonics
            Ylms.attributes['ROOT'] = attributes
            # output data to file
            args = (
                MODEL.upper(),
                LMAX,
                order_str,
                Ylms.month,
                suffix[DATAFORM],
            )
            output_file = output_dir.joinpath(output_file_format.format(*args))
            Ylms.to_file(output_file, format=DATAFORM)
            # set the permissions level of the output file to MODE
            output_file.chmod(mode=MODE)
            # append to list of output files
            output_list.append(output_file)

    # output file format for spherical harmonic data
    args = (MODEL.upper(), LMAX, order_str, suffix[DATAFORM])
    pattern = r'{0}_CLM_L{1:d}{2}_(\d+).{3}'.format(*args)
    regex = re.compile(pattern, re.VERBOSE)
    # find all output harmonic files (not just ones created in run)
    output_files = [f for f in output_dir.iterdir() if regex.match(f.name)]
    for fi in sorted(output_files):
        # extract GRACE month
        (grace_month,) = np.array(regex.findall(fi.name), dtype=int)
        YY, MM = gravtk.time.grace_to_calendar(grace_month)
        (tdec,) = gravtk.time.convert_calendar_decimal(YY, MM)
        # print date, GRACE month and calendar month to date file
        fid1.write(f'{tdec:11.6f} {grace_month:03d} {MM:02.0f}\n')
        # print output file to index
        full_output_file = gravtk.spatial().compressuser(fi)
        print(full_output_file, file=fid2)
    # close the date and index files
    fid1.close()
    fid2.close()
    # set the permissions level of the output date and index files to MODE
    output_date_file.chmod(mode=MODE)
    output_index_file.chmod(mode=MODE)
    # return the list of output files
    return output_list


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


# PURPOSE: read land sea mask to get indices of oceanic values
def ncdf_landmask(FILENAME, MASKNAME, OCEAN):
    # get logger
    logger = logging.getLogger(__name__)
    logger.debug(str(FILENAME))
    with netCDF4.Dataset(FILENAME, 'r') as fileID:
        landsea = np.squeeze(fileID.variables[MASKNAME][:].copy())
    return np.nonzero(landsea == OCEAN)


# PURPOSE: create argument parser
def arguments():
    parser = argparse.ArgumentParser(
        description="""Reads atmospheric surface pressure fields from
            reanalysis and calculates sets of spherical harmonics
            using a thin-layer 2D realistic Earth geometry
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
    now = datetime.datetime.now()
    parser.add_argument(
        '--year',
        '-Y',
        type=int,
        nargs='+',
        default=range(2000, now.year + 1),
        help='Years of model outputs to run',
    )
    # start and end years to run for mean
    parser.add_argument(
        '--mean',
        metavar=('START', 'END'),
        type=int,
        nargs=2,
        default=[2001, 2002],
        help='Start and end year range for mean',
    )
    # uniformly redistribute pressure values over the ocean
    parser.add_argument(
        '--redistribute',
        default=False,
        action='store_true',
        help='Redistribute pressure values over the ocean',
    )
    # maximum spherical harmonic degree and order
    parser.add_argument(
        '--lmax',
        '-l',
        type=int,
        default=60,
        help='Maximum spherical harmonic degree',
    )
    parser.add_argument(
        '--mmax',
        '-m',
        type=int,
        default=None,
        help='Maximum spherical harmonic order',
    )
    # different treatments of the load Love numbers
    # 0: Han and Wahr (1995) values from PREM
    # 1: Gegout (2005) values from PREM
    # 2: Wang et al. (2012) values from PREM
    # 3: Wang et al. (2012) values from PREM with hard sediment
    # 4: Wang et al. (2012) values from PREM with soft sediment
    parser.add_argument(
        '--love',
        '-n',
        type=int,
        default=0,
        choices=[0, 1, 2, 3, 4],
        help='Treatment of the Load Love numbers',
    )
    # option for setting reference frame for gravitational load love number
    # reference frame options (CF, CM, CE)
    parser.add_argument(
        '--reference',
        type=str.upper,
        default='CF',
        choices=['CF', 'CM', 'CE'],
        help='Reference frame for load Love numbers',
    )
    # input and output data format (ascii, netCDF4, HDF5)
    parser.add_argument(
        '--format',
        '-F',
        type=str,
        default='netCDF4',
        choices=['ascii', 'netCDF4', 'HDF5'],
        help='Input and output data format',
    )
    # Output log file for each job in forms
    # validrun_2002-04-01T00:00:00_PID-00000.log
    # failedrun_2002-04-01T00:00:00_PID-00000.log
    parser.add_argument(
        '--log',
        default=False,
        action='store_true',
        help='Output log file for each job',
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

    # log the command line parameters
    info(args)
    # for each reanalysis model
    for MODEL in args.model:
        # run program with parameters
        try:
            output_files = reanalysis_pressure_harmonics(
                args.directory,
                MODEL,
                args.year,
                RANGE=args.mean,
                REDISTRIBUTE=args.redistribute,
                LMAX=args.lmax,
                MMAX=args.mmax,
                LOVE_NUMBERS=args.love,
                REFERENCE=args.reference,
                DATAFORM=args.format,
                MODE=args.mode,
            )
        except:
            # if there has been an error exception
            # print the type, value, and stack trace of the
            # current exception being handled
            logger.critical(f'process id {os.getpid():d} failed')
            logger.error(traceback.format_exc())
            if args.log:  # write failed job completion log file
                logfile = gravtk.utilities.create_log_file(
                    'failedrun',
                    filename=pathlib.Path(sys.argv[0]).name,
                    arguments=vars(args),
                    model=MODEL,
                )
                logger.info(logfile)
        else:
            if args.log:  # write successful job completion log file
                logfile = gravtk.utilities.create_log_file(
                    'validrun',
                    filename=pathlib.Path(sys.argv[0]).name,
                    arguments=vars(args),
                    output=output_files,
                    model=MODEL,
                )
                logger.info(logfile)


# run main program
if __name__ == '__main__':
    main()
