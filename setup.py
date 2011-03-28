#!/usr/bin/env python

from distutils.core import setup
import setuptools

setup(
    name = "geoiq",
    packages = ["geoiq"],
    version = "0.0",
    description = "GeoIQ REST API wrapper in Python",
    author = "TODO",
    author_email = "TODO",
    url="TODO",
    requires = ["simplejson","poster"],
    long_description = """\
GeoIQ Rest API for Python.

GeoIQ includes a full Application Programming Interface (API) that
allows developers to build unique and powerful domain specific
applications. The API provides capability for uploading and download
data, searching for data and maps, building, embedding, and theming
maps or charts, as well as general user, group, and permissions
management.
"""
)
