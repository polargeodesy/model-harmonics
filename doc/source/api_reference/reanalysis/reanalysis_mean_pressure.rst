===============================
``reanalysis_mean_pressure.py``
===============================

- Calculates the mean surface pressure fields from reanalysis

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/reanalysis/reanalysis_mean_pressure.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.reanalysis.reanalysis_mean_pressure
    :func: arguments
    :prog: reanalysis_mean_pressure.py
    :nodescription:
    :nodefault:

    model : @after
        * `ERA-Interim <http://apps.ecmwf.int/datasets/data/interim-full-moda>`_
        * `ERA5 <http://apps.ecmwf.int/data-catalogues/era5/?class=ea>`_
        * `MERRA-2 <https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/>`_
        * `NCEP-DOE-2 <https://www.esrl.noaa.gov/psd/data/gridded/data.ncep.reanalysis2.html>`_
        * `NCEP-CFSR <https://rda.ucar.edu/datasets/ds093.1/>`_
        * `JRA-55 <http://jra.kishou.go.jp/JRA-55/index_en.html>`_
