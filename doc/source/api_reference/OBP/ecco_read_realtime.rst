=========================
``ecco_read_realtime.py``
=========================

- Reads 12-hour `ECCO ocean bottom pressure data from JPL <https://ecco.jpl.nasa.gov/drive/files/NearRealTime/Readme>`_
- Global area average of each ocean bottom pressure map is removed :cite:p:`Greatbatch:1994dx`
- Calculates monthly anomalies on an equirectangular grid

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/OBP/ecco_read_realtime.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.OBP.ecco_read_realtime
    :func: arguments
    :prog: ecco_read_realtime.py
    :nodescription:
    :nodefault:

    model : @after
        * ``'kf080i'``: Kalman filter analysis
        * ``'dr080i'``: RTS smoother analysis
