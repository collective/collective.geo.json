# -*- coding: utf-8 -*-
from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
import collective.geo.json


FIXTURE = PloneWithPackageLayer(zcml_filename="configure.zcml",
                                zcml_package=collective.geo.json,
                                additional_z2_products=[],
                                gs_profile_id='collective.geo.json:default',
                                name="collective.geo.json:FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,),
                                 name="collective.geo.json:Integration")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,),
                               name="collective.geo.json:Functional")
