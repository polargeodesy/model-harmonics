=========================
Terrestrial Water Storage
=========================

Models
======

GLDAS
-----

Uses `GLDAS model outputs <https://ldas.gsfc.nasa.gov/gldas>`_ from the NASA Goddard Space Flight Center (GSFC) Hydrological Sciences Laboratory (HSL) `Global Land Data Assimilation System Version 2 (GLDAS-2) <https://disc.gsfc.nasa.gov/information/data-release?title=New%20and%20Reprocessed%20GLDAS%20Version%202%20Data%20Products%20Released>`_ :cite:p:`Rodell:2004ke`.
GLDAS outputs are downloaded using the :py:mod:`gesdisc_gldas_sync.py` program.
GLDAS version 2.1 is forced with a combination of model and observation data.
Additionally, the GLDAS project produces two months of "early production stream" products that are run without the forcing data.
Here, monthly terrestrial water storage (TWS) estimates are calculated by combining the soil moisture (``SoilMoist``), snow water equivalent (``SWE``) and total canopy storage (``CanopInt``) outputs.

ERA5-Land
---------

Uses `ERA5-Land model outputs <https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-monthly-means>`_ computed by ECMWF.
ERA5-Land outputs are downloaded using the :py:mod:`cds_land_retrieve.py` program following the `cdsapi <https://cds.climate.copernicus.eu/api-how-to>`_ documentation.
Here, monthly terrestrial water storage (TWS) estimates are calculated by combining the soil moisture (``swvl1``, ``swvl2``, ``swvl3``, ``swvl4``), snow water equivalent (``sd`` and ``snowc``) and skin reservoir (``src``) outputs.

Background
==========

Monthly anomalies in terrestrial water storage are calculated by removing a multi-annual mean (typically 2003 |ndash| 2007).
Before converting to spherical harmonics, the terrestrial water storage estimates are masked to remove `urbanized <https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/TWS/gldas_mask_vegetation.py>`_, `glaciated <https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/TWS/gldas_mask_arctic.py>`_ and `permafrost <https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/TWS/gldas_mask_permafrost.py>`_ regions.
Terrestrial water storage anomalies are converted to spherical harmonics following :cite:t:`Wahr:1998hy` [Equation :ref:`4.1 <eq:2.1>`].

.. math::
    :label: 4.1
    :name: eq:4.1

	\left\{\begin{matrix}\tilde{C}_{lm}(t) \\[-4pt] \tilde{S}_{lm}(t) \end{matrix} \right\} =
	\frac{3}{4\pi a\rho_{e}}\frac{1+k_l}{2l+1}\int\sigma(\theta,\phi,t)~P_{lm}(\cos\theta)
	\left\{\begin{matrix}\cos{m\phi} \\[-4pt] \sin{m\phi} \end{matrix} \right\}~d\Omega

Framework
=========

.. graphviz::
    :caption: GLDAS Spherical Harmonics Framework
    :align: center

    digraph {
        E [label="GLDAS Land Surface\nModel Outputs"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="#7570b3"]
        L [label="Vegetation and\nLand Surface Masks"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="#7570b3"]
        M [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/TWS/gldas_mean_monthly.py"
            label="Calculate Temporal Mean"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="gray"]
        R [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/TWS/gldas_read_monthly.py"
            label="Calculate Monthly Anomalies"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="gray"]
        H [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/TWS/gldas_monthly_harmonics.py"
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
