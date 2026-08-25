=================================
``model_harmonics.greens_kernel``
=================================

- Calculate a Green's function kernel for a given set of Love Numbers

Calling Sequence
################

.. code-block:: python

    from model_harmonics.greens_kernel import greens_kernel
    X, Y, G = greens_kernel(LMAX, WIDTH=[Wx,Wy], SPACING=[dx,dy], LOVE=(hl,kl,ll))

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/greens_kernel.py

.. autofunction:: model_harmonics.greens_kernel
