=========================
``gesdisc_gldas_sync.py``
=========================

- Syncs GLDAS monthly datafiles from the Goddard Earth Sciences Data and Information Server Center (GES DISC)

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/datasets/gesdisc_gldas_sync.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.datasets.gesdisc_gldas_sync
    :func: arguments
    :prog: gesdisc_gldas_sync.py
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

    --temporal -T : @after
        * ``'M'``: Monthly
        * ``'3H'``: 3-hourly
