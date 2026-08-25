=============================
``jpl_ecco_realtime_sync.py``
=============================

- Syncs ECCO Near Real-Time model outputs from the `NASA JPL ECCO Drive server <https://ecco.jpl.nasa.gov/drive/files/NearRealTime/Readme>`_

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/datasets/jpl_ecco_realtime_sync.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.datasets.jpl_ecco_realtime_sync
    :func: arguments
    :prog: jpl_ecco_realtime_sync.py
    :nodescription:
    :nodefault:

    model : @after
        * ``'kf080i'``: Kalman filter analysis
        * ``'dr080i'``: RTS smoother analysis
