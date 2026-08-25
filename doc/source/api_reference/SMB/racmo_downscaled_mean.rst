============================
``racmo_downscaled_mean.py``
============================

- Calculates the temporal mean of downscaled RACMO surface mass balance products

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/SMB/racmo_downscaled_mean.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.SMB.racmo_downscaled_mean
    :func: arguments
    :prog: racmo_downscaled_mean.py
    :nodescription:
    :nodefault:

    --product -P : @after
        * ``'PRECIP'``: Precipitation
        * ``'REFREEZE'``: Meltwater Refreeze
        * ``'RUNOFF'``: Meltwater Runoff
        * ``'SMB'``: Surface Mass Balance
        * ``'SNOWMELT'``: Snowmelt
