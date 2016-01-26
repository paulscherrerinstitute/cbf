#!/usr/bin/env python


from setuptools import setup, find_packages, Extension

VERSION = (1, 0, 4)
VERSION_STR = ".".join([str(x) for x in VERSION])

setup(
    name='cbf',
    version=VERSION_STR,
    description="CBF Bindings for Python",
    author="Paul Scherrer Institute",
    # long_description=open('Readme.md', 'r').read(),
    url='https://github.com/paulscherrerinstitute/cbf',
    packages=['.'],
    package_dir={'': '.'},
    ext_modules=[
        Extension('cbf_c', [
            'src/cbf.cpp',
            'src/python-cbf.c'
        ], extra_compile_args=[
            "-lstdc++",
            "-O3",
            "-Wall",
            "-W",
            "-Wundef",
            "-DVERSION=\"%s\"" % VERSION_STR,
            "-DCBF_VERSION=\"0.0.1\"",
        ])
    ],

    classifiers=[
        'Programming Language :: C',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
)
