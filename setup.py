# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from cryptools import __author__, __version__, __license__

setup(
        name = 'cryptools',
        version = __version__,
        description = 'Usefull crypto tools for CTF',
        license = __license__,
        author = __author__,
        packages = find_packages(),
        install_requires = ['pycrypto', 'gmpy'],
    )
