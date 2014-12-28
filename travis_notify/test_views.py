import unittest

from pyramid import testing


class TravisAuthorizationCheckTests(unittest.TestCase):

    def _getTargetClass(self):
        from .views import TravisAuthorizationCheck
        return TravisAuthorizationCheck

    def _makeOne(self, val, config):
        return self._getTargetClass()(val, config)

    def test_ctor_w_val_None(self):
        klass = self._getTargetClass()
        config = DummyConfig()
        config.settings[klass.DEFAULT_TOKEN_KEY] = 'TOKEN'
        tac = self._makeOne(None, config)
        self.assertEqual(tac.key, klass.DEFAULT_TOKEN_KEY)
        self.assertEqual(tac.token, 'TOKEN')

    def test_ctor_w_explicit_val(self):
        config = DummyConfig(my_token='TOKEN')
        tac = self._makeOne('my_token', config)
        self.assertEqual(tac.key, 'my_token')
        self.assertEqual(tac.token, 'TOKEN')

    def test___call___wo_headers(self):
        config = DummyConfig(my_token='TOKEN')
        tac = self._makeOne('my_token', config)
        context = testing.DummyResource()
        request = testing.DummyRequest()
        self.assertFalse(tac(context, request))

    def test___call___wo_Authorization_header(self):
        from pyramid.httpexceptions import HTTPForbidden
        config = DummyConfig(my_token='TOKEN')
        tac = self._makeOne('my_token', config)
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.headers['Travis-Repo-Slug'] = 'owner/repo'
        self.assertRaises(HTTPForbidden, tac, context, request)

    def test___call___wo_TRS_header(self):
        from pyramid.httpexceptions import HTTPForbidden
        config = DummyConfig(my_token='TOKEN')
        tac = self._makeOne('my_token', config)
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.headers['Authorization'] = 'DEADBEEF'
        self.assertRaises(HTTPForbidden, tac, context, request)

    def test___call___w_headers_mismatched(self):
        from pyramid.httpexceptions import HTTPForbidden
        config = DummyConfig(my_token='TOKEN')
        tac = self._makeOne('my_token', config)
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.headers['Travis-Repo-Slug'] = 'owner/repo'
        request.headers['Authorization'] = 'DEADBEEF'
        self.assertRaises(HTTPForbidden, tac, context, request)

    def test___call___w_headers_matched(self):
        from hashlib import sha256
        config = DummyConfig(my_token='TOKEN')
        tac = self._makeOne('my_token', config)
        context = testing.DummyResource()
        request = testing.DummyRequest()
        request.headers['Travis-Repo-Slug'] = 'owner/repo'
        expected = sha256(('owner/repo' + 'TOKEN').encode('ascii')).hexdigest()
        request.headers['Authorization'] = expected
        self.assertTrue(tac(context, request))


class WebhookTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request, **kw):
        from .views import webhook
        return webhook(context, request, **kw)

    def test_it(self):
        from json import dumps
        from .models import Root
        PAYLOAD = {}
        _called_with = []
        def _mailer(registry, owner, repo, payload):
            _called_with.append((registry, owner, repo, payload))
        context = Root()
        request = testing.DummyRequest()
        request.headers['Travis-Repo-Slug'] = 'owner/repo'
        request.POST['payload'] = dumps(PAYLOAD)
        info = self._callFUT(context, request, mailer=_mailer)
        self.assertEqual(list(context['owner']['repo']), [PAYLOAD])
        self.assertEqual(_called_with,
                         [(request.registry, 'owner', 'repo', PAYLOAD)])


class HomePage(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request):
        from .views import home_page
        return home_page(context, request)

    def test_it(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['owners'], [])


class Test_includeme(unittest.TestCase):

    def _callFUT(self, config):
        from .views import includeme
        return includeme(config)

    def test_it(self):
        from .views import TravisAuthorizationCheck
        config = DummyConfig()
        self._callFUT(config)
        self.assertEqual(config._view_predicates,
                         {'travis_auth_check': TravisAuthorizationCheck})

class DummyConfig(object):

    def __init__(self, **kw):
        self.settings = kw.copy()
        self._view_predicates = {}

    def add_view_predicate(self, name, predicate):
        self._view_predicates[name] = predicate
