# -*- coding: utf-8 -*-
from collective.geo.geographer.interfaces import IGeoreferenceable
from collective.geo.geographer.interfaces import IWriteGeoreferenced
from collective.geo.json.testing import INTEGRATION
from collective.geo.settings.interfaces import IGeoFeatureStyle
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import alsoProvides
import unittest2 as unittest


class TestDocument(unittest.TestCase):

    layer = INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory("Document", "doc")
        self.doc = self.portal.doc
        alsoProvides(self.doc, IGeoreferenceable)
        self.geo = IWriteGeoreferenced(self.doc)
        self.geo.setGeoInterface('Point', (5.583, 50.633))
        self.doc.reindexObject(idxs=['zgeo_geometry', 'collective_geo_styles'])

    def test_view(self):
        geojson_view = getMultiAdapter(
            (self.doc, self.doc.REQUEST),
            name='geo-json.json'
        )
        geojson = geojson_view.__of__(self.portal)()
        self.failUnless(geojson)
        self.assertTrue('{"type": "Point", "coordinates": [5.583, 50.633]}' in geojson)

    def test_custom_styles(self):

        registry = getUtility(IRegistry)
        registry['collective.geo.settings.interfaces.IGeoFeatureStyle.linewidth'] = float(3.0)

        manager = IGeoFeatureStyle(self.doc, None)
        manager.set('use_custom_styles', False)
        manager.set('linewidth', float(11.0))
        self.doc.reindexObject(idxs=['zgeo_geometry', 'collective_geo_styles'])
        geojson_view = getMultiAdapter(
            (self.doc, self.doc.REQUEST),
            name='geo-json.json'
        )
        geojson = geojson_view.__of__(self.portal)()
        self.assertTrue('"width": 3.0' in geojson)

        manager.set('use_custom_styles', True)
        self.doc.reindexObject(idxs=['zgeo_geometry', 'collective_geo_styles'])
        geojson_view = getMultiAdapter(
            (self.doc, self.doc.REQUEST),
            name='geo-json.json'
        )
        geojson = geojson_view.__of__(self.portal)()
        self.assertTrue('"width": 11.0' in geojson)

    def test_marker_image(self):
        manager = IGeoFeatureStyle(self.doc, None)
        manager.set('marker_image', 'test.png')
        manager.set('use_custom_styles', True)
        geojson_view = getMultiAdapter(
            (self.doc, self.doc.REQUEST),
            name='geo-json.json'
        )
        geojson = geojson_view.__of__(self.portal)()
        self.assertTrue('"image": "http://nohost/plone/test.png"' in geojson)
