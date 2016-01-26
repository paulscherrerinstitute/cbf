# Overview
CBF is a simple Python package for reading and writing cbf files.

# Installation

## PYPI

```
pip install cbf
```

## Anaconda

```
conda install -c https://conda.anaconda.org/paulscherrerinstitute cbf
```

# Usage

* Read CBF file

```python
import cbf
content = cbf.read('example.cbf')

numpy_array_with_data = content.data
header_metadata = content.metadata
```

* Write CBF file

```python
import cbf
cbf.write(numpy_array)
```
