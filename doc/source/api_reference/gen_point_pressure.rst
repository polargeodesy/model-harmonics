======================================
``model_harmonics.gen_point_pressure``
======================================

- Calculates gravitational spherical harmonic coefficients for pressure values at individual points assuming a disc geometry :cite:p:`Boy:2005el,Swenson:2002kf`

Calling Sequence
################

.. code-block:: python

    from model_harmonics.gen_point_pressure import gen_point_pressure
    Ylms = gen_point_pressure(P, G, R, lon, lat, AREA=AREA, LMAX=LMAX, LOVE=(hl,kl,ll))

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/gen_point_pressure.py

.. autofunction:: model_harmonics.gen_point_pressure
