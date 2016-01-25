#include <Python.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include "cbf.h"
#include "python-cbf.h"

static PyObject *py_cbf_compress(PyObject *self, PyObject *args) {
  const unsigned char *source;
  int source_size;
  unsigned char *dest;
  int dest_size;
  int compressed_size;

  if (!PyArg_ParseTuple(args, "s#s#", &source, &source_size, &dest, &dest_size)) {
      return NULL;
  }

  compressed_size = encodeCBFuin32(source, source_size, dest, dest_size);

  return Py_BuildValue("i", compressed_size);
}


static PyObject *py_cbf_uncompress(PyObject *self, PyObject *args) {
    const unsigned char *source;
    int source_size;
    unsigned char *dest;
    int dest_size;


    if (!PyArg_ParseTuple(args, "s#s#", &source, &source_size, &dest, &dest_size)) {
        return NULL;
    }

    decodeCBFuin32(source, source_size, dest);

    return Py_BuildValue("i", 0);
}

static PyMethodDef CBFMethods[] = {
    {"compress",  py_cbf_compress, METH_VARARGS, COMPRESS_DOCSTRING},
    {"uncompress",  py_cbf_uncompress, METH_VARARGS, UNCOMPRESS_DOCSTRING},
    {NULL, NULL, 0, NULL}
};


struct module_state {
    PyObject *error;
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif

#if PY_MAJOR_VERSION >= 3

static int myextension_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int myextension_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}


static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "cbf_c",
        NULL,
        sizeof(struct module_state),
        CBFMethods,
        NULL,
        myextension_traverse,
        myextension_clear,
        NULL
};

#define INITERROR return NULL
PyObject *PyInit_cbf_c(void)

#else
#define INITERROR return
void initcbf_c(void)

#endif
{
#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
#else
    PyObject *module = Py_InitModule("cbf_c", CBFMethods);
#endif
    struct module_state *st = NULL;

    if (module == NULL) {
        INITERROR;
    }
    st = GETSTATE(module);

    st->error = PyErr_NewException("cbf.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }

    PyModule_AddStringConstant(module, "VERSION", VERSION);
    PyModule_AddStringConstant(module, "__version__", VERSION);
    PyModule_AddStringConstant(module, "CBF_VERSION", CBF_VERSION);

#if PY_MAJOR_VERSION >= 3
    return module;
#endif
}
