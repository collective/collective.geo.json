# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.3'

setup(name='collective.geo.json',
      version=version,
      description="Collective Geo GeoJson output",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          'Development Status :: 4 - Beta',
          'Operating System :: OS Independent',
      ],
      keywords='GIS JSON',
      author='Christian Ledermann',
      author_email='christian.ledermann@gmail.com',
      url='https://github.com/collective/collective.geo.json',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.geo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'collective.geo.geographer',
          'collective.geo.settings',
          'collective.geo.contentlocations',
          'geojson',
          'pygeoif',
          'plone.api'
      ],
      extras_require={
          'test': [
              'plone.app.testing',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
