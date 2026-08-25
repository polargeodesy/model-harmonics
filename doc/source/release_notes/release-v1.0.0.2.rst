.. _release-v1.0.0.2:

====================
`Release v1.0.0.2`__
====================

* ``feat``: variance off mean as error in harmonic operators
* ``feat``: add GSFC MERRA hybrid SMB `(#13) <https://github.com/polargeodesy/model-harmonics/pull/13>`_
* ``docs``: add documentation for merra hybrid `(#13) <https://github.com/polargeodesy/model-harmonics/pull/13>`_
* ``feat``: use crs to get PS standard parallel `(#13) <https://github.com/polargeodesy/model-harmonics/pull/13>`_
* ``feat``: additionally output surface mass balance anomalies `(#13) <https://github.com/polargeodesy/model-harmonics/pull/13>`_
* ``feat``: add from file in merra hybrid harmonics `(#13) <https://github.com/polargeodesy/model-harmonics/pull/13>`_
* ``fix``: fix output MERRA hybrid harmonics file name `(#13) <https://github.com/polargeodesy/model-harmonics/pull/13>`_
* ``feat``: add option for setting input format of the mascon files `(#13) <https://github.com/polargeodesy/model-harmonics/pull/13>`_
* ``feat``: add default land-sea mask for mascons `(#13) <https://github.com/polargeodesy/model-harmonics/pull/13>`_
* ``fix``: calculate MERRA hybrid grid areas if not internal
* ``fix``: output suffix in MERRA-hybrid harmonics
* ``fix``: fix output file version for 1.1
* ``fix``: fix masked array for fill values
* ``feat``: add regrid of MERRA-2 hybrid variables
* ``docs``: add documentation about regrid program
* ``fix``: add scikit-learn to dependencies
* ``fix``: use original FDM file for ais M2-hybrid products
* ``ci``: install proj from source for cartopy deps `(#14) <https://github.com/polargeodesy/model-harmonics/pull/14>`_
* ``feat``: include special case of the pole when calculating polar stereographic areas `(#14) <https://github.com/polargeodesy/model-harmonics/pull/14>`_
* ``feat``: use GRACE/GRACE-FO month to calendar month converters `(#14) <https://github.com/polargeodesy/model-harmonics/pull/14>`_
* ``feat``: add version program `(#14) <https://github.com/polargeodesy/model-harmonics/pull/14>`_
* ``fix``: suppress warnings in merra hybrid harmonics `(#14) <https://github.com/polargeodesy/model-harmonics/pull/14>`_
* ``fix``: MERRA-2 SMB harmonics to address  `#15 <https://github.com/polargeodesy/model-harmonics/issues/15>`_ `(#16) <https://github.com/polargeodesy/model-harmonics/pull/16>`_
* ``refactor``: using python logging for handling verbose output `(#16) <https://github.com/polargeodesy/model-harmonics/pull/16>`_
* ``feat``: add ERA5 mean, cumulative and harmonic P-E programs `(#17) <https://github.com/polargeodesy/model-harmonics/pull/17>`_
* ``feat``: added option to retrieve specific ERA5 surface variables `(#17) <https://github.com/polargeodesy/model-harmonics/pull/17>`_
* ``feat``: add ERA5 mean, cumulative and harmonic programs `(#17) <https://github.com/polargeodesy/model-harmonics/pull/17>`_
* ``fix``: add ncdf_expver to reduce 4d ERA5 `(#17) <https://github.com/polargeodesy/model-harmonics/pull/17>`_
* ``feat``: finish updating ERA5 programs `(#17) <https://github.com/polargeodesy/model-harmonics/pull/17>`_
* ``fix``: use calendar to grace function to calculate month in ERA harmonics
* ``fix``: convert ERA5 P-E from m/day to m/month
* ``fix``: fix logging with output files
* ``feat``: more MERRA-2 products `(#18) <https://github.com/polargeodesy/model-harmonics/pull/18>`_
* ``feat``: include sublimation from snow surface `(#18) <https://github.com/polargeodesy/model-harmonics/pull/18>`_
* ``docs``: add references to harmonics `(#18) <https://github.com/polargeodesy/model-harmonics/pull/18>`_
* ``feat``: add RACMO SMB programs `(#19) <https://github.com/polargeodesy/model-harmonics/pull/19>`_
* ``refactor``: using python logging for handling verbose output `(#20) <https://github.com/polargeodesy/model-harmonics/pull/20>`_
* ``docs``: add notes `(#20) <https://github.com/polargeodesy/model-harmonics/pull/20>`_
* ``refactor``: open MERRA-2 hybrid product options to address  `#21 <https://github.com/polargeodesy/model-harmonics/issues/21>`_ `(#22) <https://github.com/polargeodesy/model-harmonics/pull/22>`_
* ``feat``: added GSFC MERRA-2 Hybrid Greenland v1.2 `(#23) <https://github.com/polargeodesy/model-harmonics/pull/23>`_
* ``feat``: can use variable loglevels for verbose output `(#24) <https://github.com/polargeodesy/model-harmonics/pull/24>`_
* ``docs``: converting docstrings to numpydoc format `(#25) <https://github.com/polargeodesy/model-harmonics/pull/25>`_
* ``refactor``: use wrapper function for reading load Love numbers `(#25) <https://github.com/polargeodesy/model-harmonics/pull/25>`_
* ``refactor``: updates from ``gravity_toolkit.utiliities`` `(#25) <https://github.com/polargeodesy/model-harmonics/pull/25>`_
* ``fix``: setup for readthedocs
* ``test``: try docker build with windows `(#26) <https://github.com/polargeodesy/model-harmonics/pull/26>`_
* ``fix``: include utf-8 encoding in reads to be windows compliant `(#26) <https://github.com/polargeodesy/model-harmonics/pull/26>`_
* ``feat``: add GIA to harmonic_operators `(#27) <https://github.com/polargeodesy/model-harmonics/pull/27>`_
* ``refactor``: lower case keyword arguments to output spatial `(#28) <https://github.com/polargeodesy/model-harmonics/pull/28>`_
* ``fix``: deprecation fixes for regular expressions `(#28) <https://github.com/polargeodesy/model-harmonics/pull/28>`_
* ``fix``: remove singleton dimensions and copy variables to output `(#28) <https://github.com/polargeodesy/model-harmonics/pull/28>`_

.. __: https://github.com/polargeodesy/model-harmonics/releases/tag/1.0.0.2
