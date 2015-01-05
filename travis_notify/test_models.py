import unittest

from pyramid import testing


class RootTests(unittest.TestCase):

    def _getTargetClass(self):
        from .models import Root
        return Root

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_empty(self):
        root = self._makeOne()
        self.assertEqual(list(root), [])

    def test_find_create_miss(self):
        from .models import Owner
        root = self._makeOne()
        item = root.find_create('nonesuch')
        self.assertTrue(isinstance(item, Owner))
        self.assertEqual(list(root), ['nonesuch'])

    def test_find_create_hit(self):
        root = self._makeOne()
        root['extant'] = extant = testing.DummyResource()
        self.assertTrue(root.find_create('extant') is extant)


class OwnerTests(unittest.TestCase):

    def _getTargetClass(self):
        from .models import Owner
        return Owner

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_empty(self):
        owner = self._makeOne()
        self.assertEqual(list(owner), [])

    def test_find_create_miss(self):
        from .models import Repo
        owner = self._makeOne()
        item = owner.find_create('nonesuch')
        self.assertTrue(isinstance(item, Repo))
        self.assertEqual(list(owner), ['nonesuch'])

    def test_find_create_hit(self):
        owner = self._makeOne()
        owner['extant'] = extant = testing.DummyResource()
        self.assertTrue(owner.find_create('extant') is extant)


class RepoTests(unittest.TestCase):

    def _getTargetClass(self):
        from .models import Repo
        return Repo

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_empty(self):
        repo = self._makeOne()
        self.assertEqual(list(repo), [])
        self.assertEqual(list(repo.recent), [])
        self.assertEqual(list(repo.archive), [])

    def test_w_archive(self):
        from appendonly import AppendStack
        repo = self._makeOne()
        repo._recent = AppendStack(1, 3)
        pushed = ['a', 'b', 'c', 'd']
        for push in pushed:
            repo.pushItem(push)
        rev = list(reversed(pushed))
        self.assertEqual(list(repo), rev)
        self.assertEqual(list(repo.recent), rev[:1])
        self.assertEqual(list(repo.archive), rev[1:])


class Test_appmaker(unittest.TestCase):

    def _callFUT(self, zodb_root):
        from .models import appmaker
        return appmaker(zodb_root)

    def test_miss(self):
        from .models import Root
        zodb_root = {}
        root = self._callFUT(zodb_root)
        self.assertTrue(isinstance(root, Root))
        self.assertEqual(zodb_root, {'app_root': root})

