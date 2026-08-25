===============================
``model_level_coefficients.py``
===============================

- Creates a netCDF4 file of reanalysis A and B coefficients for model levels
- Model level coefficients are obtained using equation 3.17 of :cite:p:`Simmons:1981jn` and the methodology of :cite:p:`Trenberth:1993fz`

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/reanalysis/model_level_coefficients.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.reanalysis.model_level_coefficients
    :func: arguments
    :prog: model_level_coefficients.py
    :nodescription:
    :nodefault:

    model : @after
        * `ERA-Interim <http://apps.ecmwf.int/datasets/data/interim-full-moda>`_
        * `ERA5 <http://apps.ecmwf.int/data-catalogues/era5/?class=ea>`_
        * `MERRA-2 <https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/>`_
