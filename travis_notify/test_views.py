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


class Test_generate_notification_mail(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request, **kw):
        from .views import generate_notification_mail
        return generate_notification_mail(context, request, **kw)

    def test_it(self):
        root = testing.DummyResource()
        owner = root['owner'] = testing.DummyResource()
        context = root['repo'] = testing.DummyResource()
        payload = {
            "id": 1,
            "number": "1",
            "status": 0,
            "started_at": "2011-11-11T11:11:12Z",
            "finished_at": "2011-11-11T11:11:13Z",
            "status_message": "Passed",
            "commit": "62aae5f70ceee39123ef",
            "branch": "master",
            "message": "the commit message",
            "compare_url":
                "https://github.com/owner/repo/compare/master...develop",
            "committed_at": "2011-11-11T11:11:11Z",
            "committer_name": "J. Random Hacker",
            "committer_email": "jrandom@example.com",
            "author_name": "J. Random Hacker",
            "author_email": "jrandom@example.com",
            "type": "push",
            "build_url": "https://travis-ci.org/owner/repo/builds/1",
        }


class Test_webook(unittest.TestCase):

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
        def _generator(registry, owner, repo, payload):
            _called_with.append((registry, owner, repo, payload))
        context = Root()
        request = testing.DummyRequest()
        request.headers['Travis-Repo-Slug'] = 'owner/repo'
        request.POST['payload'] = dumps(PAYLOAD)
        info = self._callFUT(context, request, generator=_generator)
        self.assertEqual(list(context['owner']['repo']), [PAYLOAD])
        self.assertEqual(_called_with,
                         [(request.registry, 'owner', 'repo', PAYLOAD)])


class Test_get_main_template(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, request):
        from .views import get_main_template
        return get_main_template(request)

    def test_it(self):
        self.config.include('pyramid_chameleon')
        mt = self._callFUT(testing.DummyRequest())
        self.assertTrue(
            mt.filename.endswith('travis_notify/templates/main.pt'))


class Test_home_page(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request):
        from .views import home_page
        return home_page(context, request)

    def test_empty(self):
        context = testing.DummyResource()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['owners'], [])

    def test_w_items(self):
        context = testing.DummyResource()
        sub = context['sub'] = testing.DummyResource()
        other = context['other'] = testing.DummyResource()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['owners'], ['other', 'sub'])


class Test_owner(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request):
        from .views import owner
        return owner(context, request)

    def test_empty(self):
        root = testing.DummyResource()
        context = root['owner1'] = testing.DummyResource()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['name'], 'owner1')
        self.assertEqual(info['repos'], [])

    def test_w_items(self):
        root = testing.DummyResource()
        context = root['owner2'] = testing.DummyResource()
        sub = context['sub'] = testing.DummyResource()
        other = context['other'] = testing.DummyResource()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['name'], 'owner2')
        self.assertEqual(info['repos'], ['other', 'sub'])


class Test_repo(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _callFUT(self, context, request):
        from .views import repo
        return repo(context, request)

    def test_empty(self):
        root = testing.DummyResource()
        owner = root['owner'] = testing.DummyResource()
        context = owner['repo1'] = testing.DummyResource()
        context.recent = []
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['name'], 'repo1')
        self.assertEqual(info['recent'], [])

    def test_w_items(self):
        root = testing.DummyResource()
        owner = root['owner'] = testing.DummyResource()
        context = owner['repo2'] = testing.DummyResource()
        recent = context.recent = [object(), object()]
        sub = context['sub'] = testing.DummyResource()
        other = context['other'] = testing.DummyResource()
        request = testing.DummyRequest()
        info = self._callFUT(context, request)
        self.assertEqual(info['name'], 'repo2')
        self.assertEqual(info['recent'], recent)


class Test_includeme(unittest.TestCase):

    def _callFUT(self, config):
        from .views import includeme
        return includeme(config)

    def test_it(self):
        from .views import TravisAuthorizationCheck
        from .views import get_main_template
        config = DummyConfig()
        self._callFUT(config)
        self.assertEqual(config._view_predicates,
                         {'travis_auth_check': TravisAuthorizationCheck})
        self.assertEqual(config._request_methods,
                         {'main_template': (get_main_template, True, True)})

class DummyConfig(object):

    def __init__(self, **kw):
        self.settings = kw.copy()
        self._view_predicates = {}
        self._request_methods = {}

    def add_view_predicate(self, name, predicate):
        self._view_predicates[name] = predicate

    def add_request_method(self, callable, name, property, reify):
        self._request_methods[name] = (callable, property, reify)
