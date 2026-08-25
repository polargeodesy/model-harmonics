.. _surface-mass-balance:

====================
Surface Mass Balance
====================

Models
======

MERRA-2
-------

Uses `MERRA-2 model outputs <https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/s>`_ from the NASA `Global Modeling and Assimilation Office (GMAO) <https://gmao.gsfc.nasa.gov/>`_, 
MERRA-2 `Vertically Integrated Diagnostics (M2TMNXINT) <https://disc.gsfc.nasa.gov/datasets/M2TMNXINT_5.12.4/summary>`_ and `Land Ice Surface Diagnostics (M2TMNXGLC) <https://disc.gsfc.nasa.gov/datasets/M2TMNXGLC_5.12.4/summary>`_ are downloaded using the :py:mod:`gesdisc_merra_sync.py` program.
For MERRA-2, monthly surface mass balance (SMB) estimates are calculated by combining the convective rain (``PRECCU``), large-scale rain (``PRECLS``), snow (``PRECSN``), evaporation (``EVAP``), and runoff over glaciated land (``RUNOFF``) variables.

ERA5
----

Uses `ERA5 model outputs <https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5>`_  computed by ECMWF.
ERA5 precipitation and evaporation outputs are downloaded using the :py:mod:`cds_reanalysis_retrieve.py` program following the `cdsapi <https://cds.climate.copernicus.eu/api-how-to>`_ documentation.
For ERA5, monthly surface mass balance (SMB) estimates are calculated by combining the total precipitation (``tp``) and evaporation (``e``) variables.
ERA5 surface mass balance estimates are not including runoff as those variables are presently `inaccurate over glaciated surfaces <https://confluence.ecmwf.int/pages/viewpage.action?pageId=208488132>`_.

Background
==========

Monthly cumulative anomalies in surface mass balance are calculated by removing a multi-annual mean (typically 1980 |ndash| 1995).
Before converting to spherical harmonics, the surface mass balance estimates are masked to isolate regions of interest.
Surface mass balance anomalies are converted to spherical harmonics following :cite:t:`Wahr:1998hy` [Equation :ref:`3.1 <eq:3.1>`].

.. math::
    :label: 3.1
    :name: eq:3.1

	\left\{\begin{matrix}\tilde{C}_{lm}(t) \\[-4pt] \tilde{S}_{lm}(t) \end{matrix} \right\} =
	\frac{3}{4\pi a\rho_{e}}\frac{1+k_l}{2l+1}\int\sigma(\theta,\phi,t)~P_{lm}(\cos\theta)
	\left\{\begin{matrix}\cos{m\phi} \\[-4pt] \sin{m\phi} \end{matrix} \right\}~d\Omega

Framework
=========

.. graphviz::
    :caption: Surface Mass Balance Spherical Harmonics Framework
    :align: center

    digraph {
        E [label="MERRA-2 Reanalysis\nModel Outputs"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="#7570b3"]
        L [label="Region Masks"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="#7570b3"]
        M [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/SMB/merra_smb_mean.py"
            label="Calculate Temporal Mean"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="gray"]
        R [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/SMB/merra_smb_cumulative.py"
            label="Calculate Cumulative Anomalies"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="gray"]
        H [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/SMB/merra_smb_harmonics.py"
            label="Calculate Spherical Harmonics"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="gray"]
        S [URL="https://github.com/polargeodesy/gravity-toolkit/blob/main/scripts/combine_harmonics.py"
            label="Spatial Maps"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="#1b9e77"]
        T [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/scripts/least_squares_mascon_timeseries.py"
            label="Time Series"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="#1b9e77"]
        E -> M [arrowsize=0.8]
        E -> R [arrowsize=0.8]
        M -> R [arrowsize=0.8]
        R -> H [arrowsize=0.8]
        L -> H [arrowsize=0.8]
        H -> S [arrowsize=0.8]
        H -> T [arrowsize=0.8]
    }

.. |ndash|    unicode:: U+2013 .. EN DASH
