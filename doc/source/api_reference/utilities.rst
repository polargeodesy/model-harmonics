=============================
``model_harmonics.utilities``
=============================

Download and management utilities for syncing time and auxiliary files

 - Adds additional functions to the `GRACE/GRACE-FO  <https://github.com/polargeodesy/gravity-toolkit/blob/main/gravity_toolkit/utilities.py>`_ ``gravity_toolkit.utilities`` module

 - Can list a directory from the `Goddard Earth Sciences Data and Information Server Center (GES DISC) <https://disc.gsfc.nasa.gov/>`_

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/utilities.py


General Methods
===============

.. autofunction:: model_harmonics.utilities.get_git_revision_hash

.. autofunction:: model_harmonics.utilities.get_git_status

.. autofunction:: model_harmonics.utilities._create_default_ssl_context

.. autofunction:: model_harmonics.utilities._create_ssl_context_no_verify

.. autofunction:: model_harmonics.utilities._set_ssl_context_options

.. autofunction:: model_harmonics.utilities.gesdisc_list

.. autofunction:: model_harmonics.utilities.cmr_filter_json

.. autofunction:: model_harmonics.utilities.cmr

.. autofunction:: model_harmonics.utilities.build_request
