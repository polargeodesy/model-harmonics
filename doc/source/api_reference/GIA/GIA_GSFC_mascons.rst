=======================
``GIA_GSFC_mascons.py``
=======================

- Calculates GIA equivalent water height corrections for GSFC mascons at the central points of each mascon

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/GIA/GIA_GSFC_mascons.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.GIA.GIA_GSFC_mascons
    :func: arguments
    :prog: GIA_GSFC_mascons.py
    :nodescription:
    :nodefault:

    --gia -G : @after
        * ``'IJ05-R2'``: Ivins R2 GIA Models :cite:p:`Ivins:2013cq`
        * ``'W12a'``: Whitehouse GIA Models :cite:p:`Whitehouse:2012jj`
        * ``'SM09'``: Simpson/Milne GIA Models :cite:p:`Simpson:2009hg`
        * ``'ICE6G'``: ICE-6G GIA Models :cite:p:`Peltier:2015bo`
        * ``'Wu10'``: Wu (2010) GIA Correction :cite:p:`Wu:2010dq`
        * ``'AW13-ICE6G'``: Geruo A ICE-6G GIA Models :cite:p:`A:2013kh`
        * ``'AW13-IJ05'``: Geruo A IJ05-R2 GIA Models :cite:p:`A:2013kh`
        * ``'Caron'``: Caron JPL GIA Assimilation :cite:p:`Caron:2018ba`
        * ``'ICE6G-D'``: ICE-6G Version-D GIA Models :cite:p:`Peltier:2018dp`
        * ``'ascii'``: reformatted GIA in ascii format
        * ``'netCDF4'``: reformatted GIA in netCDF4 format
        * ``'HDF5'``: reformatted GIA in HDF5 format
