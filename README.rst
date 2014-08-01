Introduction
============

Some web mapping clients like Leaflet_ or Polymaps_ accept json as an
input format. This product produces it.

It does not have any user interface, it just provides a GeoJson_ view
for contentitems, folders and collections. To test just append
`/@@geo-json.json` to the url.

Links
=====

- Code repository: https://github.com/collective/collective.geo.json
- Questions and comments to collectivegeo-discussion@lists.coactivate.org
- Report bugs at https://github.com/collective/collective.geo.json/issues


.. _GeoJson: http://www.geojson.org/
.. _Polymaps: http://polymaps.org/
.. _Leaflet: http://leafletjs.com/

Tests
=====

This package is tested using Travis CI. The current status is :

.. image:: https://travis-ci.org/collective/collective.geo.json.svg
    :target: https://travis-ci.org/collective/collective.geo.json
