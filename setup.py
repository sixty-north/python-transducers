# Transducer's setup.py

import io
import os
import re

from setuptools import setup


def read(*names, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open('README.rst', 'r') as readme:
    long_description = readme.read()


setup(
    name = "transducer",
    packages = ["transducer"],
    version = find_version("transducer/__init__.py"),
    description = "Transducers, similar to those in Clojure",
    author = "Sixty North AS",
    author_email = "rob@sixty-north.com",
    url = "https://github.com/sixty-north/python-transducers",
    keywords = ["Python", "functional"],
    license="MIT License",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        ],
    requires = [],
    long_description = long_description
)
