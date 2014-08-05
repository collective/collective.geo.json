# -*- coding: utf-8 -*-
import unittest2 as unittest
from zope.component import getMultiAdapter
from collective.geo.json.testing import INTEGRATION
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.interface import alsoProvides
from collective.geo.geographer.interfaces import IGeoreferenceable
from collective.geo.geographer.interfaces import IWriteGeoreferenced


class TestCollection(unittest.TestCase):

    layer = INTEGRATION

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.portal.invokeFactory("Document", "doc")
        self.doc = self.portal.doc
        alsoProvides(self.doc, IGeoreferenceable)
        geo = IWriteGeoreferenced(self.doc)
        geo.setGeoInterface('Point', (5.683, 50.643))
        self.doc.reindexObject(idxs=['zgeo_geometry', 'collective_geo_styles'])

        self.portal.invokeFactory("Document", "doc2")
        self.doc2 = self.portal.doc2
        alsoProvides(self.doc2, IGeoreferenceable)
        geo2 = IWriteGeoreferenced(self.doc2)
        geo2.setGeoInterface('Point', (5.583, 50.633))
        self.doc2.reindexObject(idxs=['zgeo_geometry', 'collective_geo_styles'])

        self.portal.invokeFactory("Collection", "collection")
        self.collection = self.portal.collection
        query = [{'i': 'portal_type',
                  'o': 'plone.app.querystring.operation.selection.is',
                  'v': ['Document']}]
        self.collection.setQuery(query)

    def test_view(self):
        geojson_view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name='geo-json.json'
        )
        geojson = geojson_view.__of__(self.portal)()
        self.failUnless(geojson)
        self.assertTrue('"coordinates": [5.683, 50.643]}' and '"coordinates": [5.583, 50.633]}' in geojson)
