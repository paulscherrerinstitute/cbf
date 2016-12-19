[![Build Status](https://travis-ci.org/paulscherrerinstitute/cbf.svg?branch=master)](https://travis-ci.org/paulscherrerinstitute/cbf)

# Overview
CBF is a simple Python package (Python 3.x) for reading and writing cbf files.

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

# Plot image with matplot lib
from matplotlib import pyplot as plt
plt.imshow(numpy_array_with_data, cmap='gray', vmax=50)
plt.show()
```

* Write CBF file

```python
import cbf
cbf.write('example.cbf', numpy_array)
```
