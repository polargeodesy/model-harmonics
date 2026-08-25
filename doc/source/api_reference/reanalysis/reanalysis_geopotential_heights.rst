======================================
``reanalysis_geopotential_heights.py``
======================================

- Reads temperature and specific humidity data to calculate geopotential height and pressure difference fields at half levels from reanalysis


`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/reanalysis/reanalysis_geopotential_heights.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.reanalysis.reanalysis_geopotential_heights
    :func: arguments
    :prog: reanalysis_geopotential_heights.py
    :nodescription:
    :nodefault:

    model : @after
        * `ERA-Interim <http://apps.ecmwf.int/datasets/data/interim-full-moda>`_
        * `ERA5 <http://apps.ecmwf.int/data-catalogues/era5/?class=ea>`_
        * `MERRA-2 <https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/>`_
