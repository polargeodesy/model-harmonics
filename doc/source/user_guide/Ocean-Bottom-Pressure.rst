.. _ocean-bottom-pressure:

=====================
Ocean Bottom Pressure
=====================

Models
======

ECCO
----

Uses outputs from the NASA-JPL `Estimating the Circulation and Climate of the Ocean (ECCO) <https://ecco-group.org/>`_ model.
For ECCO near real-time Kalman-filtered (kf080i) and Rauch-Tung-Striebel (RTS) smoother (dr080i) models, reads 12-hour ocean bottom pressure data (OBP) and calculates monthly averages.
For ECCO version 4 models, reads monthly ocean bottom pressure potential anomalies and converts to estimates of absolute ocean bottom pressure (OBP).
Near real-time models are downloaded using the :py:mod:`jpl_ecco_realtime_sync.py` program, monthly Cube92 models are calculated using the :py:mod:`jpl_ecco_cube92_sync.py` program, interpolated Version 4 models are downloaded using the :py:mod:`jpl_ecco_v4_sync.py` program, and monthly Version 4 and 5 models in LLC tile format are downloaded using the :py:mod:`jpl_ecco_llc_sync.py` program.

Background
==========

Boussinesq-type models conserve volume rather than mass, and so the global area average of each monthly map is removed :cite:p:`Greatbatch:1994dx`.
Monthly anomalies in ocean bottom pressure are calculated by removing a multi-annual mean (typically 2003 |ndash| 2007).
Ocean bottom pressure anomalies are converted to spherical harmonics following :cite:t:`Boy:2005el` [Equations :ref:`2.1 <eq:2.1>` and :ref:`2.2 <eq:2.2>`].

.. math::
    :label: 2.1
    :name: eq:2.1

	\left\{\begin{matrix}\tilde{C}_{lm}(t) \\ \tilde{S}_{lm}(t) \end{matrix} \right\} =
	\frac{3}{4\pi a\rho_{e}}\frac{1+k_l}{(2l+1)}\int \xi_l(\theta,\phi,t)~P_{lm}(\cos\theta)
	\left\{\begin{matrix}\cos{m\phi} \\ \sin{m\phi} \end{matrix} \right\}\,d\Omega

.. math::
    :label: 2.2
    :name: eq:2.2

	\xi_l(\theta,\phi,t) = \left(\frac{a +  N(\theta,\phi) - d(\theta,\phi)}{a}\right)^{l+2}\frac{p_{bot}(\theta,\phi,t)}{g(\theta,\phi)}

Framework
=========

.. graphviz::
    :caption: ECCO Spherical Harmonics Framework
    :align: center

    digraph {
        E [label="ECCO Ocean Bottom Pressure"
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
        B [label="Ocean Bathymetry"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="#7570b3"]
        M [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/OBP/ecco_mean_realtime.py"
            label="Calculate Temporal Mean"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="gray"]
        R [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/OBP/ecco_read_realtime.py"
            label="Calculate Monthly Anomalies"
            fontname="Lato"
            fontsize=11
            shape=box
            style="filled"
            color="gray"]
        H [URL="https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/OBP/ecco_monthly_harmonics.py"
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
        M -> R [arrowsize=0.8]
        E -> R [arrowsize=0.8]
        R -> H [arrowsize=0.8]
        N -> H [arrowsize=0.8]
        B -> H [arrowsize=0.8]
        H -> S [arrowsize=0.8]
        H -> T [arrowsize=0.8]
    }

.. |ndash|    unicode:: U+2013 .. EN DASH
