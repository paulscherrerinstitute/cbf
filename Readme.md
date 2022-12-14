[![python_test](https://github.com/paulscherrerinstitute/cbf/actions/workflows/python_test.yaml/badge.svg)](https://github.com/paulscherrerinstitute/cbf/actions/workflows/python_test.yaml)
[![pypi_publish](https://github.com/paulscherrerinstitute/cbf/actions/workflows/pypi_publish.yaml/badge.svg)](https://github.com/paulscherrerinstitute/cbf/actions/workflows/pypi_publish.yaml)


# Overview
CBF is a simple Python package (Python 3.x) for reading and writing cbf (Crystallographic Binary Format) files.

# Installation

## PYPI

```
pip install cbf
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
