========================
``jpl_ecco_llc_sync.py``
========================

- Syncs ECCO Version 4 and 5 LLC tile model outputs from the `NASA JPL ECCO Drive server <https://ecco.jpl.nasa.gov/drive/files/Version5/Alpha/nctiles_monthly>`_
- Errata document for `Version 4, Revision 4 Atmospheric Pressure Forcing <https://ecco-group.org/docs/ECCO_V4r4_errata.pdf>`_

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/datasets/jpl_ecco_llc_sync.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.datasets.jpl_ecco_llc_sync
    :func: arguments
    :prog: jpl_ecco_llc_sync.py
    :nodescription:
    :nodefault:

    model : @after
        * ``'V4r4'``: Version 4, Revision 4
        * ``'V5alpha'``: ECCO Version 5, Alpha release
