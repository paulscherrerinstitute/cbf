# Overview
CBF is a simple Python package for reading and writing cbf files.

# Installation

# Usage

* Read CBF file

```python
import cbf
content = cbf.read('test.cbf')

numpy_array_with_data = content.data
header_metadata = content.metadata
```

* Write CBF file

```python
import cbf
cbf.write(numpy_array)
```


# Packaging
## PYPI
Build Package

```
python setup.py bdist
```

Install Package

```
pip install -e .
```

## Anaconda
To build the Anaconda package do following steps:

* Commit all changes to Git
* Tag Git repository
* Push all commits and tags to the central repository

```bash
git push
git push --tags
```

* Go to the `utils/conda_package` directory
* Build the anaconda package

```bash
conda build cbf
```

* Copy the generated package to the central package server (Adapt the filename and architecture!)

```bash
cp ~/conda-bld/linux-64/cbf-1.0.0-np19py27_0.tar.bz2 /afs/psi.ch/service/conda-pkg/linux-64/
```

* Index the central package server (Adapt the architecture folder!)

```bash
conda index /afs/psi.ch/service/conda-pkg/linux-64/
```

* Now the package can be installed via `conda install cbf`
