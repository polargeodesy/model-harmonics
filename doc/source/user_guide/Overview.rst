========
Overview
========

This documentation is intended to explain how to compute spherical harmonics from model
outputs for comparing with or correcting time-variable gravity measurements from the
`GRACE/GRACE-FO <https://github.com/polargeodesy/gravity-toolkit>`_ missions.
This software was developed with the goal of supporting science applications for
time-variable gravity.

The ``model-harmonics`` projects consists of extension routines for the set of ``gravity-toolkit`` tools.

Components
==========

.. plot:: ./user_guide/components.py
    :caption: Schematic from :cite:t:`Sutterley:2019bx` of major mass transport processes observed using time-variable gravity measurements
    :align: center

.. grid:: 2 2 4 4
    :padding: 0

    .. grid-item-card::  Atmospheric Circulation
      :text-align: center
      :link: ./Atmospheric-Circulation.html

      :material-outlined:`air;5em`

    .. grid-item-card::  Ocean Bottom Pressure
      :text-align: center
      :link: ./Ocean-Bottom-Pressure.html

      :material-outlined:`water;5em`

    .. grid-item-card::  Surface Mass Balance
      :text-align: center
      :link: ./Surface Mass Balance.html

      :material-outlined:`ac_unit;5em`

    .. grid-item-card::  Terrestrial Water Storage
      :text-align: center
      :link: ./Terrestrial-Water-Storage.html

      :material-outlined:`water_drop;5em`


.. toctree::
    :hidden:
    :maxdepth: 1
    :numbered: 3

    ./Atmospheric-Circulation.rst
    ./Ocean-Bottom-Pressure.rst
    ./Surface-Mass-Balance.rst
    ./Terrestrial-Water-Storage.rst
