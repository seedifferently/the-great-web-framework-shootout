# -*- coding: utf-8 -*-
"""
Global configuration file for TG2-specific settings in HelloWorld.

This file complements development/deployment.ini.

Please note that **all the argument values are strings**. If you want to
convert them into boolean, for example, you should use the
:func:`paste.deploy.converters.asbool` function, as in::
    
    from paste.deploy.converters import asbool
    setting = asbool(global_conf.get('the_setting'))
 
"""

from tg.configuration import AppConfig

import helloworld
from helloworld import model
from helloworld.lib import app_globals, helpers 

base_config = AppConfig()
base_config.renderers = []

base_config.package = helloworld

base_config.use_dotted_templatenames = False
base_config.default_renderer = 'jinja'
base_config.renderers.append('jinja')
#base_config.renderers.append('genshi')
#base_config.renderers.append('mako')
#base_config.renderers.append('json')

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = helloworld.model
base_config.DBSession = helloworld.model.DBSession

#No need for tosca in this test app
base_config.use_toscawidgets = False
