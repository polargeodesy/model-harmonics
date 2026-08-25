====================================
``reanalysis_pressure_harmonics.py``
====================================

- Reads atmospheric surface pressure fields from reanalysis and calculates sets of spherical harmonics using a thin-layer 2D geometry with realistic earth :cite:p:`Boy:2005el,Swenson:2002kf`

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/reanalysis/reanalysis_pressure_harmonics.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.reanalysis.reanalysis_pressure_harmonics
    :func: arguments
    :prog: reanalysis_pressure_harmonics.py
    :nodescription:
    :nodefault:

    model : @after
        * `ERA-Interim <http://apps.ecmwf.int/datasets/data/interim-full-moda>`_
        * `ERA5 <http://apps.ecmwf.int/data-catalogues/era5/?class=ea>`_
        * `MERRA-2 <https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/>`_
        * `NCEP-DOE-2 <https://www.esrl.noaa.gov/psd/data/gridded/data.ncep.reanalysis2.html>`_
        * `NCEP-CFSR <https://rda.ucar.edu/datasets/ds093.1/>`_
        * `JRA-55 <http://jra.kishou.go.jp/JRA-55/index_en.html>`_

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
