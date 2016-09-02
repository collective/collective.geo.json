# -*- coding: utf-8 -*-
from zope.interface import implements, Interface
from zope.component import getUtility
from zope.tales.tales import CompilerError

from Products.Five import BrowserView
try:
    from shapely.geometry import asShape
except:
    from pygeoif.geometry import as_shape as asShape

import geojson

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression, getExprContext

from plone.registry.interfaces import IRegistry

from collective.geo.geographer.interfaces import IGeoreferenced
from collective.geo.settings.interfaces import IGeoFeatureStyle
from collective.geo.mapwidget import utils
from collective.geo.json import logger


def get_marker_image(context, marker_img):
    try:
        marker_img = Expression(str(marker_img))(getExprContext(context))
    except CompilerError:
        logger.info("Could not parse expression {}".format(marker_img))
        marker_img = '{}/{}'.format(context.portal_url(), marker_img)
    return marker_img


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
            tc = int(color, 16)
            if len(color) == 3:
                color = ''.join([b * 2 for b in color]) + '3c'
            elif len(color) == 4:
                color = ''.join([b * 2 for b in color])
            elif len(color) == 6:
                color = color + '3c'
            elif len(color) == 8:
                pass
            else:
                raise ValueError, "input #%s is not in #RRGGBB[AA] format" % color
            return color
        return 'AABBCCDD'

    def _get_style(self, geo_type):
        style = {}
        if self.styles:
            if not geo_type.get('type', None):
                return style
            fill = self.normalize_color(self.styles['polygoncolor'])
            stroke = self.normalize_color(self.styles['linecolor'])
            if geo_type['type'].endswith('Polygon'):
                style['fill'] = fill
                style['stroke'] = stroke
                style['width'] = self.styles['linewidth']
            elif geo_type['type'].endswith('LineString'):
                style['stroke'] = stroke
                style['width'] = self.styles['linewidth']
            elif geo_type['type'].endswith('Point'):
                self.styles['marker_image']
                style['fill'] = fill
                style['stroke'] = stroke
                style['width'] = self.styles['linewidth']
                if self.styles.get('marker_image', None):
                    img = get_marker_image(self.context,
                                           self.styles['marker_image'])
                    style['image'] = img
                else:
                    style['image'] = None
        return style

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')


class JsonDocument(JsonBaseDocument):

    def __call__(self):
        self.request.RESPONSE.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        try:
            geometry = IGeoreferenced(self.context)
        except:
            return '{}'
        try:
            self.styles = utils.get_feature_styles(self.context)
        except:
            self.styles = None
        if geometry.geo['type']:
            classes = geometry.geo['type'].lower() + ' '
        else:
            classes = ''
        classes += self.context.getPhysicalPath()[-2].replace('.', '-')
        json_result = [
            geojson.Feature(
                id=self.context.id.replace('.', '-'),
                geometry=geometry.geo,
                properties={
                    "title": self.context.Title(),
                    "description": self.context.Description(),
                    "style": self._get_style(geometry.geo),
                    "url": self.context.absolute_url(),
                    "classes": classes,
                })]
        return geojson.dumps(geojson.FeatureCollection(json_result))


class JsonFolderDocument(JsonBaseDocument):

    def get_brains(self):
        querydict = {}
        querydict['path'] = {'query': '/'.join(self.context.getPhysicalPath())}
        return self.portal_catalog(querydict)

    def get_json(self):
        json_result = []
        for brain in self.get_brains():
            if brain.zgeo_geometry:
                self.styles = brain.collective_geo_styles
                geom = {'type': brain.zgeo_geometry['type'],
                        'coordinates': brain.zgeo_geometry['coordinates']}
                if geom['coordinates']:
                    if geom['type']:
                        classes = geom['type'].lower() + ' '
                    else:
                        classes = ''
                    classes += brain.getPath().split('/')[-2].replace('.', '-')
                    json_result.append(
                        geojson.Feature(
                            id=brain.id.replace('.', '-'),
                            geometry=asShape(geom),
                            style=self._get_style(geom),
                            properties={
                                "title": brain.Title,
                                "description": brain.Description,
                                "style": self._get_style(geom),
                                "url": brain.getURL(),
                                "classes": classes,
                            }))
        feature_collection = geojson.FeatureCollection(json_result)
        feature_collection.update({'title': self.context.title})
        return geojson.dumps(feature_collection)

    def __call__(self):
        self.request.RESPONSE.setHeader('Content-Type',
                                        'application/json; charset=utf-8')
        return self.get_json()


class JsonTopicDocument(JsonFolderDocument):

    def get_brains(self):
        return self.context.queryCatalog()


class JsonCollectionDocument(JsonTopicDocument):

    def get_brains(self):
        return self.context.queryCatalog()
