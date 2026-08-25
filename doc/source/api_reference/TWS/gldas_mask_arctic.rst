========================
``gldas_mask_arctic.py``
========================

- Creates a mask for GLDAS data for Greenland, Svalbard, Iceland and the Russian High Arctic defined by a set of shapefiles

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/TWS/gldas_mask_arctic.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.TWS.gldas_mask_arctic
    :func: arguments
    :prog: gldas_mask_arctic.py
    :nodescription:
    :nodefault:

    --spacing -S : @after
        * ``'10'``: 1.0 degrees latitude/longitude
        * ``'025'``: 0.25 degrees latitude/longitude

