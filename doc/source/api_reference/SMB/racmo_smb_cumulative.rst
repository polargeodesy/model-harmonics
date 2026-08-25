===========================
``racmo_smb_cumulative.py``
===========================

- Reads RACMO datafiles to calculate cumulative anomalies in derived surface mass balance products

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/SMB/racmo_smb_cumulative.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.SMB.racmo_smb_cumulative
    :func: arguments
    :prog: racmo_smb_cumulative.py
    :nodescription:
    :nodefault:

    --product -P : @after
        * ``'precip'``: Precipitation
        * ``'rainfall'``: Rainfall
        * ``'refreeze'``: Meltwater Refreeze
        * ``'runoff'``: Meltwater Runoff
        * ``'smb'``: Surface Mass Balance
        * ``'sndiv'``: Snow Drift Erosion
        * ``'snowfall'``: Snowfall
        * ``'snowmelt'``: Snowmelt
        * ``'subl'``: Sublimation
