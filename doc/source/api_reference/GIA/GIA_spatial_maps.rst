=======================
``GIA_spatial_maps.py``
=======================

- Calculates spatial maps of Glacial Isostatic Adjustment (GIA)

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/GIA/GIA_spatial_maps.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.GIA.GIA_spatial_maps
    :func: arguments
    :prog: GIA_spatial_maps.py
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

    --units -U : @after
        * ``1``: cm of water thickness
        * ``2``: mm of geoid height
        * ``4``: |mu|\ Gal gravitational perturbation
        * ``5``: mbar equivalent surface pressure
        * ``6``: cm viscoelastic crustal uplift

    --interval : @replace
        Output grid interval

        * ``1``: (0:360, 90:-90)
        * ``2``: (degree spacing/2)
        * ``3``: non-global grid (set with defined bounds)

.. |mu|      unicode:: U+03BC .. GREEK SMALL LETTER MU

.. |times|      unicode:: U+00D7 .. MULTIPLICATION SIGN
