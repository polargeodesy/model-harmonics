=========================
``gesdisc_merra_sync.py``
=========================

- Syncs MERRA-2 surface mass balance (SMB) related products from the Goddard Earth Sciences Data and Information Server Center (GES DISC)
- ``tavgM_2d_int`` (Vertically Integrated Diagnostics) collection:

    * ``PRECCU`` (convective rain)
    * ``PRECLS`` (large-scale rain)
    * ``PRECSN`` (snow)
    * ``EVAP`` (evaporation)
- ``tavgM_2d_glc`` (Land Ice Surface Diagnostics) collection:

    * ``RUNOFF`` (runoff over glaciated land)

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/datasets/gesdisc_merra_sync.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.datasets.gesdisc_merra_sync
    :func: arguments
    :prog: gesdisc_merra_sync.py
    :nodescription:
    :nodefault:
