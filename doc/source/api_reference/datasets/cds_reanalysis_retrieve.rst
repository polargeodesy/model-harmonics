==============================
``cds_reanalysis_retrieve.py``
==============================

- Retrieves ERA5 reanalysis netCDF4 datasets from the CDS Web API

    * 2-metre Temperature (t2m)
    * Surface Pressure (ps)
    * Mean Sea Level Pressure (msl)
    * Temperature (t) and Specific Humidity (q) on Model Levels
    * Invariant Parameters

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/datasets/cds_reanalysis_retrieve.py

.. argparse::
    :module: model_harmonics.datasets.cds_reanalysis_retrieve
    :func: arguments
    :prog: cds_reanalysis_retrieve.py
    :nodescription:
    :nodefault:

    --surface -S : @after
        * ``'MSL'``: mean sea level pressure field
        * ``'SP'``: surface pressure field
        * ``'T2m'``: 2-metre temperature field
        * ``'P-E'``: precipitation and evaporation fields
