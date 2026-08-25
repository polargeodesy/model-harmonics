.. _atmospheric-circulation:

=======================
Atmospheric Circulation
=======================

Reanalysis
==========

ECMWF
-----

`ERA-Interim <https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era-interim>`_ is computed by ECMWF and is available starting from 1979.
`ERA5 <https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5>`_  is the latest reanalysis computed by ECMWF offering much higher spatial and temporal resolution and is available starting from 1950.
Differences between ERA-Interim and ERA5 are outlined `here <https://confluence.ecmwf.int/pages/viewpage.action?pageId=74764925>`_.
ERA5 outputs are downloaded using the :py:mod:`cds_reanalysis_retrieve.py` program following the `cdsapi <https://cds.climate.copernicus.eu/api-how-to>`_ documentation.
:py:mod:`ecmwf_reanalysis_retrieve.py` uses the newer `ecmwf-datastores-client <https://ecmwf.github.io/ecmwf-datastores-client>`_ that may replace the CDS api in the future.

Dimensions
^^^^^^^^^^

- ``latitude``: latitude
- ``longitude``: longitude
- ``lvl``: model level
- ``valid_time``: time

Variables
^^^^^^^^^

- ``z``: geopotential height
- ``msl``: sea level pressure
- ``q``: specific humidity
- ``sp``: surface pressure
- ``t``: temperature


JRA
----

`JRA-55 <http://jra.kishou.go.jp/JRA-55/index_en.html>`_ is computed by the Japan Meteorological Agency (JMA) and is available starting from 1958.
`JRA-3Q <https://www.data.jma.go.jp/jra/html/JRA-3Q/index_en.html>`_ is the successor to JRA-55 and covers three quarters of a century :cite:p:`Kosaka:2024ib`.
JRA-55 and JRA-3Q outputs are downloaded using the :py:mod:`ucar_gdex_jra55_surface.py` and :py:mod:`ucar_gdex_jra3q_surface.py` programs.

Dimensions
^^^^^^^^^^

- ``lat``: latitude
- ``lon``: longitude
- ``time``: time

Variables
^^^^^^^^^

- ``z`` (JRA-55) / ``gp-sfc-cn-gauss`` (JRA-3Q): geopotential height
- ``sp`` (JRA-55) / ``pres-sfc-an-gauss`` (JRA-3Q): surface pressure


MERRA-2
--------

NASA's Modern-Era Retrospective analysis for Research and Applications (`MERRA-2 <https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/>`_) is computed by the Global Modeling and Assimilation Office (GMAO) and is available starting from 1980.
MERRA-2 outputs are downloaded using the :py:mod:`gesdisc_merra_subset.py` (for 2-dimensional) or :py:mod:`gesdisc_merra_monthly.py` (for 3-dimensional) programs.

Dimensions
^^^^^^^^^^

- ``lat``: latitude
- ``lon``: longitude
- ``lev``: model level
- ``time``: time

Variables
^^^^^^^^^

- ``PHIS``: geopotential height
- ``PS``: surface pressure
- ``QV``: specific humidity
- ``SLP``: sea level pressure
- ``T``: temperature


NCEP
----

`NCEP-DOE-2 <https://www.esrl.noaa.gov/psd/data/gridded/data.ncep.reanalysis2.html>`_ is computed by the National Centers for Environmental Prediction (NCEP) and is available starting from 1979.
NCEP-DOE-2 outputs are downloaded using the :py:mod:`noaa_cdc_ncep_ftp.py` program.
`NCEP-CFSR <https://cfs.ncep.noaa.gov/>`_ is computed by the National Centers for Environmental Prediction (NCEP) and is available starting from 1979 with Version 2 available from 2011 onward.
Both versions of NCEP-CFSR outputs are downloaded using the :py:mod:`ucar_gdex_cfsr_surface.py` program.

Dimensions
^^^^^^^^^^

- ``lat``: latitude
- ``lon``: longitude
- ``time``: time

Variables
^^^^^^^^^

- ``hgt`` (NCEP-DOE-2) / ``orog`` (NCEP-CFSR): geopotential height
- ``pres`` (NCEP-DOE-2) / ``ave_sp`` (NCEP-CFSR): surface pressure


Background
==========

Anomalies for each reanalysis are calculated relative to a multi-annual mean (such as 2003 |ndash| 2014).
Spherical harmonics from reanalysis outputs are computed here using three different schemes of complexity following :cite:t:`Boy:2005el,Swenson:2002kf`:

1. a thin-layer 2D spherical geometry
2. a thin-layer 2D geometry with realistic geometry incorporating model orography and estimates of geoid height [Equations :ref:`1.1 <eq:1.1>` and :ref:`1.2 <eq:1.2>`]
3. a 3D atmospheric geometry integrating over the model layers [Equations :ref:`1.1 <eq:1.1>` and :ref:`1.3 <eq:1.3>`].

.. math::
    :label: 1.1
    :name: eq:1.1

	\left\{\begin{matrix}\tilde{C}_{lm}(t) \\ \tilde{S}_{lm}(t) \end{matrix} \right\} =
	\frac{3}{4\pi a\rho_{e}}\frac{1+k_l}{(2l+1)}\int \xi_l(\theta,\phi,t)~P_{lm}(\cos\theta)
	\left\{\begin{matrix}\cos{m\phi} \\ \sin{m\phi} \end{matrix} \right\}\,d\Omega

.. math::
    :label: 1.2
    :name: eq:1.2

	\xi_l(\theta,\phi,t) = \left(\frac{a + h(\theta,\phi) + N(\theta,\phi)}{a}\right)^{l+2}\frac{p_0(\theta,\phi,t)}{g(\theta,\phi)}

.. math::
    :label: 1.3
    :name: eq:1.3

	\xi_l(\theta,\phi,t) = -\int_{p_0}^{0}\left(\frac{a + z(\theta,\phi) + N(\theta,\phi)}{a}\right)^{l+2}\frac{dp}{g(\theta,\phi,z)}


Framework
=========

.. graphviz::
    :caption: Reanalysis Spherical Harmonics with Two-Dimensional Geometry Framework
    :align: center

    digraph {
        E [label="Reanalysis Surface Pressure"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="#7570b3"]
        N [label="Geoid Height"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="#7570b3"]
        O [label="Model Orography"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="#7570b3"]
        M [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/reanalysis/reanalysis_mean_pressure.py"
            label="Calculate Temporal Mean"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="gray"]
        H [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/reanalysis/reanalysis_pressure_harmonics.py"
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
        M -> H [arrowsize=0.8]
        E -> H [arrowsize=0.8]
        N -> H [arrowsize=0.8]
        O -> H [arrowsize=0.8]
        H -> S [arrowsize=0.8]
        H -> T [arrowsize=0.8]
    }

.. graphviz::
    :caption: Reanalysis Spherical Harmonics with Three-Dimensional Geometry Framework
    :align: center

    digraph {
        E [label="Reanalysis Temperature\nand Specific Humidity"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="#7570b3"]
        L [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/reanalysis/model_level_coefficients.py"
            label="Model Level\nCoefficients"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="#7570b3"]
        N [label="Geoid Height"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="#7570b3"]
        O [label="Model Orography"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="#7570b3"]
        G [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/reanalysis/reanalysis_geopotential_heights.py"
            label="Calculate Geopotential Heights\nand Pressure Differences"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="gray"]
        M [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/reanalysis/reanalysis_mean_harmonics.py"
            label="Calculate Temporal Mean\nSpherical Harmonics"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="gray"]
        H [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/reanalysis/reanalysis_atmospheric_harmonics.py"
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
        E -> G [arrowsize=0.8]
        L -> G [arrowsize=0.8]
        O -> G [arrowsize=0.8]
        G -> M [arrowsize=0.8]
        M -> H [arrowsize=0.8]
        G -> H [arrowsize=0.8]
        N -> H [arrowsize=0.8]
        H -> S [arrowsize=0.8]
        H -> T [arrowsize=0.8]
    }

.. |ndash|    unicode:: U+2013 .. EN DASH
