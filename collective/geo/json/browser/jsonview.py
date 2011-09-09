from zope.interface import implements, Interface
from Products.Five import BrowserView
from shapely.geometry import asShape
import geojson
from collective.geo.geographer.interfaces import IGeoreferenced


class IJsonDocument(Interface):
    ''' Marker Interface '''


class JsonBaseDocument(BrowserView):
    implements(IJsonDocument)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')


class JsonDocument(BrowserView):

    def __call__(self):
        try:
            geometry = IGeoreferenced(self.context)
        except:
            return ''
        json_result = [
                geojson.Feature(
                    id=self.context.id,
                    geometry=geometry.geo,
                    properties={
                        "title": self.context.Title(),
                        "description": self.context.Description()
                        })]

        self.request.RESPONSE.setHeader('Content-Type','application/json; charset=utf-8')
        return geojson.dumps(geojson.FeatureCollection(json_result))

class JsonFolderDocument(BrowserView):

    def __call__(self):
        json_result = []
        for brain in self.context.getFolderContents():
            if brain.zgeo_geometry:
                geom = { 'type': brain.zgeo_geometry['type'],
                            'coordinates': brain.zgeo_geometry['coordinates']}
                if geom['coordinates']:
                    json_result.append(
                         geojson.Feature(
                            id=brain.id,
                            geometry=asShape(geom),
                            properties={
                                "title": brain.Title,
                                "description": brain.Description
                                }))
        self.request.RESPONSE.setHeader('Content-Type','application/json; charset=utf-8')
        return geojson.dumps(geojson.FeatureCollection(json_result))

class JsonTopicDocument(BrowserView):

    def __call__(self):
        json_result = []
        for brain in self.context.queryCatalog():
            if brain.zgeo_geometry:
                geom = { 'type': brain.zgeo_geometry['type'],
                            'coordinates': brain.zgeo_geometry['coordinates']}
                if geom['coordinates']:
                    json_result.append(
                         geojson.Feature(
                            id=brain.id,
                            geometry=asShape(geom),
                            properties={
                                "title": brain.Title,
                                "description": brain.Description
                                }))
        self.request.RESPONSE.setHeader('Content-Type','application/json; charset=utf-8')
        return geojson.dumps(geojson.FeatureCollection(json_result))
