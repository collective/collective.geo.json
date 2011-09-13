from zope.interface import implements, Interface
from zope.component import getUtility
from Products.Five import BrowserView
from shapely.geometry import asShape
import geojson
from plone.registry.interfaces import IRegistry
from collective.geo.geographer.interfaces import IGeoreferenced
from collective.geo.settings.interfaces import IGeoFeatureStyle


class IJsonDocument(Interface):
    ''' Marker Interface '''


class JsonBaseDocument(BrowserView):
    implements(IJsonDocument)

    defaultstyles = None
    styles = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        registry = getUtility(IRegistry)
        self.defaultstyles = registry.forInterface(IGeoFeatureStyle)

    def _get_style(self, geo_type):
        style= {'color': None,
                'width': None,
                'image': None}
        if self.defaultstyles:
            if geo_type['type'].endswith('Polygon'):
                style['color'] = self.defaultstyles.polygoncolor
            elif geo_type['type'].endswith('LineString'):
                style['color'] = self.defaultstyles.linecolor
                style['width'] = self.defaultstyles.linewidth
            elif geo_type['type'].endswith('Point'):
                style['image']= self.defaultstyles.marker_image
        if self.styles:
            if self.styles['use_custom_styles']:
                if geo_type['type'].endswith('Polygon'):
                    style['color'] = self.styles['polygoncolor']
                elif geo_type['type'].endswith('LineString'):
                    style['color'] = self.styles['linecolor']
                    style['width'] = self.styles['linewidth']
                elif geo_type['type'].endswith('Point'):
                    style['image']= self.styles['marker_image']
        return style

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')


class JsonDocument(JsonBaseDocument):

    def __call__(self):
        self.request.RESPONSE.setHeader('Content-Type','application/json; charset=utf-8')
        try:
            geometry = IGeoreferenced(self.context)
        except:
            return '{}'
        try:
            self.styles = IGeoFeatureStyle(self.context).geostyles
        except:
            self.styles = None
        json_result = [
                geojson.Feature(
                    id=self.context.id,
                    geometry=geometry.geo,
                    properties={
                        "title": self.context.Title(),
                        "description": self.context.Description(),
                        "style": self._get_style(geometry.geo),
                        "url": self.context.absolute_url()
                        })]
        return geojson.dumps(geojson.FeatureCollection(json_result))

class JsonFolderDocument(JsonBaseDocument):

    def __call__(self):
        json_result = []
        for brain in self.context.getFolderContents():
            if brain.zgeo_geometry:
                self.styles = brain.collective_geo_styles
                geom = { 'type': brain.zgeo_geometry['type'],
                            'coordinates': brain.zgeo_geometry['coordinates']}
                if geom['coordinates']:
                    json_result.append(
                         geojson.Feature(
                            id=brain.id,
                            geometry=asShape(geom),
                            properties={
                                "title": brain.Title,
                                "description": brain.Description,
                                "style": self._get_style(geom),
                                "url": brain.getURL(),
                                }))
        self.request.RESPONSE.setHeader('Content-Type','application/json; charset=utf-8')
        return geojson.dumps(geojson.FeatureCollection(json_result))

class JsonTopicDocument(JsonBaseDocument):

    def __call__(self):
        json_result = []
        for brain in self.context.queryCatalog():
            if brain.zgeo_geometry:
                self.styles = brain.collective_geo_styles
                geom = { 'type': brain.zgeo_geometry['type'],
                            'coordinates': brain.zgeo_geometry['coordinates']}
                if geom['coordinates']:
                    json_result.append(
                         geojson.Feature(
                            id=brain.id,
                            geometry=asShape(geom),
                            properties={
                                "title": brain.Title,
                                "description": brain.Description,
                                "style": self._get_style(geom),
                                "url": brain.getURL(),
                                }))
        self.request.RESPONSE.setHeader('Content-Type','application/json; charset=utf-8')
        return geojson.dumps(geojson.FeatureCollection(json_result))
