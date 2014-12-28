from appendonly import AppendStack
from appendonly import Archive
from persistent import Persistent
from repoze.folder import Folder
import transaction


class Root(Folder):

    __parent__ = __name__ = None

    def find_create(self, name):
        if name not in self:
            owner = self[name] = Owner()
            owner.__name__ = name
            owner.__parent__ = self
        return self[name]

class Owner(Folder):

    def find_create(self, name):
        if name not in self:
            repo = self[name] = Repo()
            repo.__name__ = name
            repo.__parent__ = self
        return self[name]


class Repo(Persistent):

    def __init__(self):
        self._recent = AppendStack()
        self._archive = Archive()

    def pushItem(self, object):
        self._stack.push(object, self._archive.addLayer)

    def __iter__(self):
        for generation, index, item in self._stack:
            yield item
        for generation, index, item in self._archive:
            yield item


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = Root()
        zodb_root['app_root'] = app_root
        transaction.commit()
    return zodb_root['app_root']
