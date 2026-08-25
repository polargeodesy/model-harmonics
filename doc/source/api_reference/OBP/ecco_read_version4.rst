=========================
``ecco_read_version4.py``
=========================

- Reads monthly ECCO ocean bottom pressure data from `Version 4 models <https://ecco-group.org/products-ECCO-V4r4.htm>`_ and calculates monthly anomalies
- Global area average of each ocean bottom pressure map is removed :cite:p:`Greatbatch:1994dx`

`Source code`__

.. __: https://github.com/polargeodesy/model-harmonics/blob/main/model_harmonics/OBP/ecco_read_version4.py

Calling Sequence
################

.. argparse::
    :module: model_harmonics.OBP.ecco_read_version4
    :func: arguments
    :prog: ecco_read_version4.py
    :nodescription:
    :nodefault:

    model : @after
        * ``'V4r3'``: Version 4, Revision 3
        * ``'V4r4'``: Version 4, Revision 4
