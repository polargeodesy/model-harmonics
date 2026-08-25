# model-harmonics

Python tools for obtaining and working with model synthetic spherical harmonic coefficients for comparing with data from the the NASA/DLR Gravity Recovery and Climate Experiment (GRACE) and the NASA/GFZ Gravity Recovery and Climate Experiment Follow-On (GRACE-FO) missions

These are extension routines for the set of [gravity-toolkit](https://github.com/polargeodesy/gravity-toolkit) tools


## About

<table>
  <tr>
    <td><b>Version:</b></td>
    <td>
        <a href="https://pypi.python.org/pypi/model-harmonics/" alt="PyPI"><img src="https://img.shields.io/pypi/v/model-harmonics.svg"></a>
        <a href="https://anaconda.org/conda-forge/model-harmonics" alt="conda-forge"><img src="https://img.shields.io/conda/vn/conda-forge/model-harmonics"></a>
        <a href="https://github.com/polargeodesy/model-harmonics/releases/latest" alt="commits-since"><img src="https://img.shields.io/github/commits-since/polargeodesy/model-harmonics/latest"></a>
    </td>
  </tr>
  <tr>
    <td><b>Citation:</b></td>
    <td>
        <a href="https://doi.org/10.5281/zenodo.5156964" alt="zenodo"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.5156964.svg"></a>
    </td>
  </tr>
  <tr>
    <td><b>Tests:</b></td>
    <td>
        <a href="https://model-harmonics.readthedocs.io/en/latest/?badge=latest" alt="Documentation Status"><img src="https://readthedocs.org/projects/model-harmonics/badge/?version=latest"></a>
        <a href="https://github.com/polargeodesy/model-harmonics/actions/workflows/python-request.yml" alt="Build"><img src="https://github.com/polargeodesy/model-harmonics/actions/workflows/python-request.yml/badge.svg"></a>
        <a href="https://github.com/polargeodesy/model-harmonics/actions/workflows/ruff-format.yml" alt="Ruff"><img src="https://github.com/polargeodesy/model-harmonics/actions/workflows/ruff-format.yml/badge.svg"></a>
    </td>
  </tr>
  <tr>
    <td><b>License:</b></td>
    <td>
        <a href="https://github.com/polargeodesy/model-harmonics/blob/main/LICENSE" alt="License"><img src="https://img.shields.io/github/license/polargeodesy/model-harmonics"></a>
    </td>
  </tr>
</table>

For more information: see the documentation at [model-harmonics.readthedocs.io](https://model-harmonics.readthedocs.io/)

## Installation

From PyPI:

```bash
python3 -m pip install model-harmonics
```

To include all optional dependencies:

```bash
python3 -m pip install model-harmonics[all]
```

Using `conda` or `mamba` from conda-forge:

```bash
conda install -c conda-forge model-harmonics
```

```bash
mamba install -c conda-forge model-harmonics
```

Development version from GitHub:

```bash
python3 -m pip install git+https://github.com/polargeodesy/model-harmonics.git
```

### Running with Pixi

Alternatively, you can use [Pixi](https://pixi.sh/) for a streamlined workspace environment:

1. Install Pixi following the [installation instructions](https://pixi.sh/latest/#installation)
2. Clone the project repository:

```bash
git clone https://github.com/polargeodesy/model-harmonics.git
```

3. Move into the `model-harmonics` directory

```bash
cd model-harmonics
```

4. Install dependencies and start a shell:

```bash
pixi shell
```

This will automatically create the environment, install all dependencies, and open a ``bash`` shell for executing programs.

## Resources

- [NASA GRACE mission site](https://www.nasa.gov/mission_pages/Grace/index.html)
- [NASA GRACE-FO mission site](https://www.nasa.gov/missions/grace-fo)
- [JPL GRACE Tellus site](https://grace.jpl.nasa.gov/)
- [JPL GRACE-FO site](https://gracefo.jpl.nasa.gov/)
- [UTCSR GRACE site](http://www.csr.utexas.edu/grace/)
- [GRACE at the NASA Physical Oceanography Distributed Active Archive Center (PO.DAAC)](https://podaac.jpl.nasa.gov/grace)
- [GRACE at the GFZ Information System and Data Center](http://isdc.gfz-potsdam.de/grace-isdc/)

## Dependencies

- [cdsapi: Python client libraries for the CDS Web API](https://pypi.org/project/cdsapi/)
- [ecmwf-datastores-client: programmatic access to the CDS, ADS and EWDS data catalogues](https://ecmwf.github.io/ecmwf-datastores-client)
- [fiona: Python wrapper for vector data access functions from the OGR library](https://fiona.readthedocs.io/en/latest/manual.html)
- [geoid-toolkit: Python utilities for calculating geoid heights from static gravity field coefficients](https://github.com/polargeodesy/geoid-toolkit/)
- [gravity-toolkit: Python tools for working with GRACE/GRACE-FO data](https://github.com/polargeodesy/gravity-toolkit/)
- [h5py: Python interface for Hierarchal Data Format 5 (HDF5)](https://www.h5py.org/)
- [netCDF4: Python interface to the netCDF C library](https://unidata.github.io/netcdf4-python/)
- [pyproj: Python interface to PROJ library](https://pypi.org/project/pyproj/)
- [shapely: PostGIS-ish operations outside a database context for Python](http://toblerity.org/shapely/index.html)
- [scikit-learn: Machine Learning in Python](https://scikit-learn.org/stable/index.html)

## Download

The program homepage is:  
<https://github.com/polargeodesy/model-harmonics>

A zip archive of the latest version is available directly at:  
<https://github.com/polargeodesy/model-harmonics/archive/main.zip>

## Disclaimer

This package includes software developed at the University of California at Irvine (UCI), the NASA Jet Propulsion Laboratory (JPL), NASA Goddard Space Flight Center (GSFC) and the University of Washington Applied Physics Laboratory (UW-APL).
This program is not sponsored or maintained by the Universities Space Research Association (USRA),
the Center for Space Research at the University of Texas (UTCSR), the Jet Propulsion Laboratory (JPL),
the German Research Centre for Geosciences (GeoForschungsZentrum, GFZ) or NASA.
The software is provided here for your convenience but *with no guarantees whatsoever*.

## Contributing

This project contains work and contributions from the [scientific community](./CONTRIBUTORS.md).
If you would like to contribute to the project, please have a look at the [contribution guidelines](./doc/source/getting_started/Contributing.rst), [open issues](https://github.com/polargeodesy/model-harmonics/issues) and [discussions board](https://github.com/polargeodesy/model-harmonics/discussions).

## References

> T. C. Sutterley, I. Velicogna, and C.-W. Hsu,
> "Self-Consistent Ice Mass Balance and Regional Sea Level From Time-Variable Gravity",
> *Earth and Space Science*, 7, (2020).
> [doi: 10.1029/2019EA000860](https://doi.org/10.1029/2019EA000860)
> 
> T. C. Sutterley and I. Velicogna,
> "Improved estimates of geocenter variability from time-variable gravity and ocean model outputs", 
> *Remote Sensing*, 11(18), 2108, (2019).
> [doi: 10.3390/rs11182108](https://doi.org/10.3390/rs11182108)

## License

The content of this project is licensed under the [Creative Commons Attribution 4.0 Attribution license](https://creativecommons.org/licenses/by/4.0/) and the source code is licensed under the [MIT license](LICENSE).
