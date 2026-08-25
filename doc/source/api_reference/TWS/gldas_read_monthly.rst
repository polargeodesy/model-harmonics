=========================
``gldas_read_monthly.py``
=========================

- Reads GLDAS monthly datafiles to calculate anomalies in total water storage from soil moisture, snow water equivalent and total canopy storage :cite:p:`Rodell:2004ke,Syed:2008ia`

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/TWS/gldas_read_monthly.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.TWS.gldas_read_monthly
    :func: arguments
    :prog: gldas_read_monthly.py
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
