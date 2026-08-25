==========================
``merra_smb_harmonics.py``
==========================

- Reads monthly MERRA-2 surface mass balance anomalies and converts to spherical harmonic coefficients :cite:p:`Wahr:1998hy`

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/SMB/merra_smb_harmonics.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.SMB.merra_smb_harmonics
    :func: arguments
    :prog: merra_smb_harmonics.py
    :nodescription:
    :nodefault:

    product : @after
        * ``'SMB'``: Surface Mass Balance
        * ``'ACCUM'``: Snowfall accumulation
        * ``'PRECIP'``: Total Precipitation
        * ``'RAINFALL'``: Total Rainfall
        * ``'SUBLIM'``: Evaporation and Sublimation
        * ``'RUNOFF'``: Meltwater Runoff

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
