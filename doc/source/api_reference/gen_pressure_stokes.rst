=======================================
``model_harmonics.gen_pressure_stokes``
=======================================

- Converts pressure fields from the spatial domain to spherical harmonic coefficients :cite:p:`Boy:2005el,Swenson:2002kf`

Calling Sequence
################

.. code-block:: python

    from model_harmonics.gen_pressure_stokes import gen_pressure_stokes
    from gravity_toolkit.associated_legendre import plm_holmes
    PLM, dPLM = plm_holmes(LMAX, np.cos(th))
    Ylms = gen_pressure_stokes(P, G, R, lon, lat, LMAX=LMAX, PLM=PLM, LOVE=(hl,kl,ll))

`Source code`__

.. __: https://github.com/polargeodesy/gravity-toolkit/blob/main/gravity_toolkit/gen_pressure_stokes.py

.. autofunction:: model_harmonics.gen_pressure_stokes
