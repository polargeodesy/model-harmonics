==========================
``racmo_smb_harmonics.py``
==========================

- Reads monthly RACMO variables and converts to spherical harmonic coefficients :cite:p:`Wahr:1998hy`
- Estimates the grid values as point masses for calculating the gravitational spherical harmonic coefficients

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/SMB/racmo_smb_harmonics.py

Calling Sequence
################

- ``model_file``: full path to input RACMO netCDF4 file

Command Line Options
####################

.. argparse::
    :module: model_harmonics.SMB.racmo_smb_harmonics
    :func: arguments
    :prog: racmo_smb_harmonics.py
    :nodescription:
    :nodefault:

    --product -P : @after
        * ``'precip'``: Precipitation
        * ``'rainfall'``: Rainfall
        * ``'refreeze'``: Meltwater Refreeze
        * ``'runoff'``: Meltwater Runoff
        * ``'smb'``: Surface Mass Balance
        * ``'sndiv'``: Snow Drift Erosion
        * ``'snowfall'``: Snowfall
        * ``'snowmelt'``: Snowmelt
        * ``'subl'``: Sublimation

    --love -n : @after
        * ``0``: Han and Wahr (1995) values from PREM :cite:p:`Han:1995go`
        * ``1``: Gegout (2005) values from PREM :cite:p:`Gegout:2010gc`
        * ``2``: Wang et al. (2012) values from PREM :cite:p:`Wang:2012gc`
        * ``3``: Wang et al. (2012) values from PREM with hard sediment :cite:p:`Wang:2012gc`
        * ``4``: Wang et al. (2012) values from PREM with soft sediment :cite:p:`Wang:2012gc`

    --reference : @after
        * ``'CF'``: Center of Surface Figure
        * ``'CM'``: Center of Mass of Earth System
        * ``'CE'``: Center of Mass of Solid Earth
