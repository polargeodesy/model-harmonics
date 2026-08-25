============================
``gldas_mask_permafrost.py``
============================

- Creates a mask for GLDAS data based on the permafrost/surface classification from the `NSIDC Circum-Arctic Map of Permafrost and Ground-Ice Conditions <http://nsidc.org/data/ggd318.html>`_

    1. Continuous Permafrost
    2. Discontinuous Permafrost
    3. Isolated Permafrost
    4. Sporadic Permafrost
    5. Glaciated Area

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/TWS/gldas_mask_permafrost.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.TWS.gldas_mask_permafrost
    :func: arguments
    :prog: gldas_mask_permafrost.py
    :nodescription:
    :nodefault:

    --spacing -S : @after
        * ``'10'``: 1.0 degrees latitude/longitude
        * ``'025'``: 0.25 degrees latitude/longitude
