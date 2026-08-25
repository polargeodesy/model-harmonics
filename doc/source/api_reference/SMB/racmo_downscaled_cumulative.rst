==================================
``racmo_downscaled_cumulative.py``
==================================

- Calculates cumulative anomalies of downscaled RACMO surface mass balance products

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/SMB/racmo_downscaled_cumulative.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.SMB.racmo_downscaled_cumulative
    :func: arguments
    :prog: racmo_downscaled_cumulative.py
    :nodescription:
    :nodefault:

    --product -P : @after
        * ``'PRECIP'``: Precipitation
        * ``'REFREEZE'``: Meltwater Refreeze
        * ``'RUNOFF'``: Meltwater Runoff
        * ``'SMB'``: Surface Mass Balance
        * ``'SNOWMELT'``: Snowmelt
