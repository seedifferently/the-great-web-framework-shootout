from pyramid.config import Configurator
from pyramid_jinja2 import renderer_factory
from sqlalchemy import engine_from_config

from helloworld.models import appmaker

def app(global_config, **settings):
    """ This function returns a WSGI application.
    """
    
    engine = engine_from_config(settings, 'sqlalchemy.')
    get_root = appmaker(engine)
    config = Configurator(settings=settings, root_factory=get_root)
    config.include('pyramid_jinja2')
#        config.add_static_view('static', 'helloworld:static', cache_max_age=3600)
    config.add_view('helloworld.views.string_hello')
    config.add_view('helloworld.views.raw_sql',
                    name='raw_sql')
    config.add_view('helloworld.views.jinja_hello',
                    name='jinja_hello',
                    renderer="hello.jinja2")
    config.add_view('helloworld.views.jinja_sql',
                    name='jinja_sql',
                    renderer="db.jinja2")
    return config.make_wsgi_app()
