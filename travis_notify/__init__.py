from pyramid.config import Configurator
from pyramid_zodbconn import get_connection
from .models import appmaker


def root_factory(request):
    conn = get_connection(request)
    return appmaker(conn.root())


def main(global_config, config=None, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    if config is None:  # pragma: no cover
        config = Configurator(root_factory=root_factory, settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.include('.views')
    config.scan()
    return config.make_wsgi_app()
