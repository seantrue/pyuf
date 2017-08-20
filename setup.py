#!/usr/bin/env python


from __future__ import absolute_import
from io import open
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name = u'pyuf',
    version = u'1.2',
    description = u'Python library for uFactory',
    author = u'Duke Fong',
    author_email = u'developer@ufactory.cc',
    url = u"https://github.com/uarm-developer/pyuf",
    keywords = u"pyuf swift uarm ufactory",
    packages = [u'uf', u'uf.ufc', u'uf.utils', u'uf.comm', u'uf.swift', u'uf.swift.grove', u'uf.uarm', u'uf.wrapper'],
    install_requires = [u'pyserial>=3.0'],
    long_description = open(u'README.md').read(),
    license = u'BSD'
)

