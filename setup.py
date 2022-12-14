#!/usr/bin/env python


from setuptools import setup, Extension
import platform

VERSION = (1, 2, 0)
VERSION_STR = ".".join([str(x) for x in VERSION])

CBF_VERSION = (0, 0, 1)
CBF_VERSION_STR = ".".join([str(x) for x in CBF_VERSION])

compile_args = []
if platform.system().lower() == "windows":
    macros = [("VERSION", '\\"%s\\"' % VERSION_STR), ("CBF_VERSION", '\\"%s\\"' % CBF_VERSION_STR)]
else:
    macros = [("VERSION", '"%s"' % VERSION_STR), ("CBF_VERSION", '"%s"' % CBF_VERSION_STR)]
    compile_args.append("-O3")

setup(
    name="cbf",
    version=VERSION_STR,
    description="CBF Bindings for Python",
    long_description="CBF Bindings for Python",
    author="Paul Scherrer Institute",
    url="https://github.com/paulscherrerinstitute/cbf",
    py_modules=["cbf"],
    ext_modules=[
        Extension("cbf_c", ["src/cbf.cpp", "src/python-cbf.c"], define_macros=macros, extra_compile_args=compile_args)
    ],
    install_requires=["numpy"],
    classifiers=["Programming Language :: C", "Programming Language :: Python", "Programming Language :: Python :: 3"],
)
