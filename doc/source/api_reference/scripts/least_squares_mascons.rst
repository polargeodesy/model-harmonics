============================
``least_squares_mascons.py``
============================

- Reads in an index of spherical harmonic coefficient files
- Filters and smooths data with specified processing algorithms :cite:p:`Jekeli:1981vj,Swenson:2006hu`
- Calculates regional mass anomalies through a least-squares mascon procedure following :cite:t:`Tiwari:2009bx,Jacob:2012gv`

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/scripts/least_squares_mascons.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.scripts.least_squares_mascons
    :func: arguments
    :prog: least_squares_mascons.py
    :nodescription:
    :nodefault:

    --love -n : @after
        * ``0``: Han and Wahr (1995) values from PREM :cite:p:`Han:1995go`
        * ``1``: Gegout (2005) values from PREM :cite:p:`Gegout:2010gc`
        * ``2``: Wang et al. (2012) values from PREM :cite:p:`Wang:2012gc`
        * ``3``: Wang et al. (2012) values from PREM with hard sediment :cite:p:`Wang:2012gc`
        * ``4``: Wang et al. (2012) values from PREM with soft sediment :cite:p:`Wang:2012gc`

    --reference : @after
        * ``'CF'``: Center of Surface Figure
        * ``'CM'``: Center of Mass of Earth System
        * ``'CE'``: Center of Mass of Solid Earth

    --fit-method : @after
        * ``1``: mass coefficients
        * ``2``: geoid coefficients

    --solver -s : @replace
        Least squares solver for degree one solutions

        * ``'inv'``: matrix inversion
        * ``'lstsq'``: least squares solution
        * ``'gelsy'``: complete orthogonal factorization solution
        * ``'gelss'``: singular value decomposition (SVD) solution
        * ``'gelsd'``: singular value decomposition (SVD) solution with a divide and conquer method
