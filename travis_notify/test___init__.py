import unittest

from pyramid import testing


class Test_root_factory(unittest.TestCase):

    def _callFUT(self, request):
        from travis_notify import root_factory
        return root_factory(request)

    def test_it(self):

        class DummyConnection(object):
            def __init__(self, root):
                self._root = root
            def root(self):
                return {'app_root': self._root}

        request = testing.DummyRequest()
        root = object()
        request._primary_zodb_conn = conn = DummyConnection(root)
        self.assertTrue(self._callFUT(request) is root)


class Test_main(unittest.TestCase):

    def _callFUT(self, global_config, config, **settings):
        from travis_notify import main
        return main(global_config, config, **settings)

    def test_it(self):
        class DummyConfigurator(object):
            def __init__(self, app):
                self._included = []
                self._static_views = {}
                self._scanned = False
                self._app = app
            def include(self, other):
                self._included.append(other)
            def add_static_view(self, name, pfx, **kw):
                self._static_views[name] = (pfx, kw)
            def scan(self):
                self._scanned = True
            def make_wsgi_app(self):
                return self._app

        app = object()
        configurator = DummyConfigurator(app)
        self.assertTrue(self._callFUT(object(), configurator) is app)
        self.assertEqual(configurator._included,
                        ['pyramid_chameleon', '.views'])
        self.assertEqual(configurator._static_views['static'],
                            ('static', {'cache_max_age': 3600}))
        self.assertTrue(configurator._scanned)

