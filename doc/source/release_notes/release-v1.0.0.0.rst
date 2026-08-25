.. _release-v1.0.0.0:

====================
`Release v1.0.0.0`__
====================

* ``feat``: add initial reanalysis download routines
* ``feat``: add initial reanalysis programs for atmospheric harmonics
* ``feat``: add NOAA CDC download
* ``feat``: add ``A`` and ``B`` coefficients function for integrating 3D model-level outputs
* ``feat``: add download routines for CFSR and JRA-55
* ``fix``: update requirements for ERA-interim and ERA5 download tools
* ``docs``: initial version of documentation
* ``docs``: some uniformity between option descriptions
* ``ci``: add flake8 workflow `(#1) <https://github.com/polargeodesy/model-harmonics/pull/1>`_
* ``docs``: expand overview to add text and equations `(#1) <https://github.com/polargeodesy/model-harmonics/pull/1>`_
* ``fix``: update requirements for new ECMWF client `(#1) <https://github.com/polargeodesy/model-harmonics/pull/1>`_
* ``feat``: add ``pygrib`` (and ``eccodes``) to dependencies for GLDAS `(#1) <https://github.com/polargeodesy/model-harmonics/pull/1>`_
* ``feat``: add merra-2 download from links list program `(#1) <https://github.com/polargeodesy/model-harmonics/pull/1>`_
* ``fix``: regular expression updates for python3 `(#1) <https://github.com/polargeodesy/model-harmonics/pull/1>`_
* ``feat``: add ECCO2 cube92 models `(#2) <https://github.com/polargeodesy/model-harmonics/pull/2>`_
* ``feat``: use ``spatial`` class to output files in cube92 sync `(#2) <https://github.com/polargeodesy/model-harmonics/pull/2>`_
* ``feat``: read from model level files in slices to reduce memory load `(#2) <https://github.com/polargeodesy/model-harmonics/pull/2>`_
* ``feat``: add ECMWF and CDS api credential options to sync programs `(#2) <https://github.com/polargeodesy/model-harmonics/pull/2>`_
* ``docs``: update documentation for Cube92 and new features `(#2) <https://github.com/polargeodesy/model-harmonics/pull/2>`_
* ``feat``: initial MERRA-2 SMB routines `(#3) <https://github.com/polargeodesy/model-harmonics/pull/3>`_
* ``refactor``: outputs from SH generators are now harmonics objects
* ``refactor``: separate 3D spherical harmonics function to separate file
* ``feat``: update ECCO Cube92 programs
* ``docs``: update documentation
* ``feat``: add GLDAS mask programs for converting to harmonics
* ``refactor``: update GLDAS harmonics program with new mask names
* ``docs``: update documentation
* ``docs``: use ``sphinx_rtd_theme`` for documentation
* ``docs``: change some markdown docs to rst
* ``refactor``: generalize ecco sync programs for different variables
* ``feat``: add GLDAS scaling factor program
* ``refactor``: separate pressure and gravity inputs to ``gen_pressure_stokes``
* ``feat``: add ECCO LLC tile programs
* ``feat``: LLC harmonics program uses sparse points and assumes a disc geometry
* ``docs``: update documentation
* ``feat``: add merra-2 mask program
* ``fix``: sort MERRA-2 files by month as September 2020 was reprocessed
* ``feat``: add MERRA-2 invariant file sync
* ``feat``: update gen point pressure to reduce dependencies/improve computational time
* ``feat``: add ``spatial_operators`` program
* ``feat``: add ``harmonic_operators`` program
* ``feat``: update GLDAS scaling factors program
* ``feat``: include GLDAS MOD44W land mask modified for HYMAP
* ``feat``: added options to truncate output to a degree or order in ``harmonic_operators``
* ``docs``: added variance off mean as estimated error in ``spatial_operators``
* ``fix``: replaced ``numpy`` bool to prevent deprecation warning
* ``feat``: add options operator programs to read from individual index files
* ``refactor``: moved model mascon programs from ``gravity-toolkit``
* ``docs``: add contribution guidelines `(#4) <https://github.com/polargeodesy/model-harmonics/pull/4>`_
* ``feat``: update cds and ecmwf sync programs `(#4) <https://github.com/polargeodesy/model-harmonics/pull/4>`_
* ``feat``: automatically update years to run based on current time
* ``feat``: add IB response from MSLP program `(#5) <https://github.com/polargeodesy/model-harmonics/pull/5>`_
* ``docs``: more documentation standardization
* ``ci``: add test suite `(#6) <https://github.com/polargeodesy/model-harmonics/pull/6>`_
* ``docs``: update documentation `(#6) <https://github.com/polargeodesy/model-harmonics/pull/6>`_
* ``feat``: set a default netrc file and check access `(#6) <https://github.com/polargeodesy/model-harmonics/pull/6>`_
* ``feat``: default credentials from environmental variables `(#6) <https://github.com/polargeodesy/model-harmonics/pull/6>`_
* ``docs``: use rst citations in documentation `(#7) <https://github.com/polargeodesy/model-harmonics/pull/7>`_
* ``fix``: update setup.py for readthedocs check `(#7) <https://github.com/polargeodesy/model-harmonics/pull/7>`_
* ``ci``: update github action workflows `(#7) <https://github.com/polargeodesy/model-harmonics/pull/7>`_
* ``docs``: update readme `(#7) <https://github.com/polargeodesy/model-harmonics/pull/7>`_
* ``docs``: add semantic commit message documentation
* ``feat``: add parser object for removing commented or empty lines `(#8) <https://github.com/polargeodesy/model-harmonics/pull/8>`_
* ``feat``: added option for connection timeout to sync programs `(#9) <https://github.com/polargeodesy/model-harmonics/pull/9>`_
* ``feat``: use try/except for retrieving netrc credentials
* ``fix``: define int/float precision to prevent deprecation warning `(#10) <https://github.com/polargeodesy/model-harmonics/pull/10>`_
* ``ci``: pin ``proj`` to v7 for ``cartopy`` install `(#10) <https://github.com/polargeodesy/model-harmonics/pull/10>`_
* ``ci``: ``homebrew`` now installs ``proj8`` by default `(#10) <https://github.com/polargeodesy/model-harmonics/pull/10>`_
* ``ci``: ``proj8`` deprecated and removed the ``proj_api.h`` header `(#10) <https://github.com/polargeodesy/model-harmonics/pull/10>`_
* ``fix``: GESDISC GLDAS sync for monthly case
* ``fix``: new date format for GESDISC MERRA SMB sync
* ``refactor``: switch from parameter files to argparse arguments `(#11) <https://github.com/polargeodesy/model-harmonics/pull/11>`_
* ``docs``: add notes about large JRA-55 requests
* ``fix``: adjust ordering of file line search in csh file for JRA-55
* ``docs``: update license badge on readme
* ``feat``: added option for retrieving the model level variables
* ``fix``: check ERA5 files for expver slice `(#12) <https://github.com/polargeodesy/model-harmonics/pull/12>`_
* ``fix``: reverse layers so bottom=0 `(#12) <https://github.com/polargeodesy/model-harmonics/pull/12>`_
* ``fix``: add try/except for pygrib import
* ``feat``: add warnings for ECCO Version 4, Revision 4
* ``docs``: add links to errata document

.. __: https://github.com/polargeodesy/model-harmonics/releases/tag/1.0.0.0
