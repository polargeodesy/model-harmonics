==========================
``ecco_mean_llc_tiles.py``
==========================

- Reads monthly ECCO ocean bottom pressure LLC tile data and calculates multi-annual means
- Global area average of each ocean bottom pressure map is removed :cite:p:`Greatbatch:1994dx`

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/OBP/ecco_mean_llc_tiles.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.OBP.ecco_mean_llc_tiles
    :func: arguments
    :prog: ecco_mean_llc_tiles.py
    :nodescription:
    :nodefault:

    model : @after
        * ``'V4r4'``: Version 4, Revision 4
        * ``'V5alpha'``: ECCO Version 5, Alpha release
