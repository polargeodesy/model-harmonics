=============================
``ecco_monthly_harmonics.py``
=============================

- Reads monthly ECCO ocean bottom pressure anomalies and converts to spherical harmonic coefficients :cite:p:`Boy:2005el`

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/OBP/ecco_monthly_harmonics.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.OBP.ecco_monthly_harmonics
    :func: arguments
    :prog: ecco_monthly_harmonics.py
    :nodescription:
    :nodefault:

    model : @after
        * ``'kf080i'``: ECCO Near Real-Time Kalman filter analysis
        * ``'dr080i'``: ECCO Near Real-Time RTS smoother analysis
        * ``'Cube92'``: ECCO2 Cube92 models
        * ``'V4r3'``: ECCO Version 4, Revision 3 models
        * ``'V4r4'``: ECCO Version 4, Revision 4 models

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
