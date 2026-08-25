==============================
``gldas_monthly_harmonics.py``
==============================

- Reads monthly GLDAS total water storage anomalies and converts to spherical harmonic coefficients :cite:p:`Wahr:1998hy`

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/TWS/gldas_monthly_harmonics.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.TWS.gldas_monthly_harmonics
    :func: arguments
    :prog: gldas_monthly_harmonics.py
    :nodescription:
    :nodefault:

    model : @after
        * ``'CLM'``: GLDAS Community Land Model
        * ``'CLSM'``: GLDAS Catchment Land Surface Model
        * ``'MOS'``: GLDAS Mosaic model
        * ``'NOAH'``: GLDAS Noah model
        * ``'VIC'``: GLDAS Variable Infiltration Capacity model

    --spacing -S : @after
        * ``'10'``: 1.0 degrees latitude/longitude
        * ``'025'``: 0.25 degrees latitude/longitude

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
