#include "Python.h"

#define COMPRESS_DOCSTRING      "Compress string, returning the compressed data.\nRaises an exception if any error occurs."
#define UNCOMPRESS_DOCSTRING    "Decompress string, returning the uncompressed data.\nRaises an exception if any error occurs."


static PyObject *py_cbf_compress(PyObject *self, PyObject *args);
static PyObject *py_cbf_uncompress(PyObject *self, PyObject *args);

PyMODINIT_FUNC initcbf_c(void);

#if defined(_WIN32) && defined(_MSC_VER)
# define inline __inline
# if _MSC_VER >= 1600
#  include <stdint.h>
# else /* _MSC_VER >= 1600 */
   typedef signed char       int8_t;
   typedef signed short      int16_t;
   typedef signed int        int32_t;
   typedef unsigned char     uint8_t;
   typedef unsigned short    uint16_t;
   typedef unsigned int      uint32_t;
# endif /* _MSC_VER >= 1600 */
#endif

#if defined(__SUNPRO_C) || defined(__hpux) || defined(_AIX)
#define inline
#endif

#ifdef __linux
#define inline __inline
#endif
