from zope.interface import implements, Interface
from zope.component import getUtility

from Products.Five import BrowserView

from shapely.geometry import asShape
import geojson

from Products.CMFCore.utils import getToolByName

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

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def normalize_color(self, color):
        if color:
            if color.startswith('#'):
                color = color[1:]
            if len(color)==3 or len(color)==4:
                color =''.join([b*2 for b in color])
            if len(color)==6:
                color = color +'3c'
            if len(color)==8:
                return color
        return 'AABBCCDD'

    def _get_style(self, geo_type):
        style= {}
        if self.styles:
            fill = self.normalize_color(self.styles['polygoncolor'])
            stroke = self.normalize_color(self.styles['linecolor'])
            if self.styles['use_custom_styles']:
                if geo_type['type'].endswith('Polygon'):
                    style['fill'] = fill
                    style['stroke'] = stroke
                    style['width'] = self.styles['linewidth']
                elif geo_type['type'].endswith('LineString'):
                    style['stroke'] = stroke
                    style['width'] = self.styles['linewidth']
                elif geo_type['type'].endswith('Point'):
                    img = self.styles['marker_image']
                    style['fill'] = fill
                    style['stroke'] =stroke
                    style['width'] = self.styles['linewidth']
                    if img.startswith('string:${portal_url}'):
                        img = self.portal.absolute_url() + img[20:]
                    style['image']= img
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
        classes = geometry.geo['type'].lower() + ' '
        classes += self.context.getPhysicalPath()[-2].replace('.','-') #+ ' '
        json_result = [
                geojson.Feature(
                    id=self.context.id.replace('.','-'),
                    geometry=geometry.geo,
                    properties={
                        "title": self.context.Title(),
                        "description": self.context.Description(),
                        "style": self._get_style(geometry.geo),
                        "url": self.context.absolute_url(),
                        "classes" : classes,
                        })]
        return geojson.dumps(geojson.FeatureCollection(json_result))

class JsonFolderDocument(JsonBaseDocument):

    def get_brain(self):
        return self.context.getFolderContents()

    def __call__(self):
        json_result = []
        for brain in self.get_brain():
            if brain.zgeo_geometry:
                self.styles = brain.collective_geo_styles
                geom = { 'type': brain.zgeo_geometry['type'],
                            'coordinates': brain.zgeo_geometry['coordinates']}
                if geom['coordinates']:
                    classes = brain.zgeo_geometry['type'].lower() + ' '
                    classes += brain.getPath().split('/')[-2].replace('.','-')
                    json_result.append(
                         geojson.Feature(
                            id=brain.id.replace('.','-'),
                            geometry=asShape(geom),
                            properties={
                                "title": brain.Title,
                                "description": brain.Description,
                                "style": self._get_style(geom),
                                "url": brain.getURL(),
                                "classes" : classes,
                                }))
        self.request.RESPONSE.setHeader('Content-Type','application/json; charset=utf-8')
        return geojson.dumps(geojson.FeatureCollection(json_result))

class JsonTopicDocument(JsonFolderDocument):

    def get_brain(self):
        return self.context.queryCatalog()

