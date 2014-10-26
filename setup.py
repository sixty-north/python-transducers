# Transducer's setup.py

from distutils.core import setup

version = 0.5

with open('README.rst', 'r') as readme:
    long_description = readme.read()

setup(
    name = "transducer",
    packages = ["transducer"],
    version = "{version}".format(version=version),
    description = "Tranducers, similar to those in Clojure",
    author = "Sixty North AS",
    author_email = "rob@sixty-north.com",
    url = "http://code.sixty-north.com/python-transducers",
    keywords = ["Python", "functional"],
    license="MIT License",
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
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
