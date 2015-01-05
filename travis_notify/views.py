from hashlib import sha256
from json import loads

from pyramid.httpexceptions import HTTPForbidden
from pyramid.renderers import get_renderer
from pyramid.view import view_config

from .models import Owner
from .models import Root
from .models import Repo

try:
    text_type = unicode
except NameError:  # pragma: no cover
    text_type = str


class TravisAuthorizationCheck(object):
    """View predicate for Travis notification token authentication

    Compare the 'Travis-Repo-Slug' header with the 'Authorization' header
    (based on a hash with a configured TRAVIS_TOKEN).

    Raise Forbidden if the are present but don't match.

    Return False if they are not present.

    Return True if they are present and match.

    See:
      http://docs.travis-ci.com/user/notifications/#Authorization-for-Webhooks

    .. note::
       This is really a permission check, mashed up with a short-circuited
       authentication polciy.
    """
    DEFAULT_TOKEN_KEY = 'travis_notify.token'

    def __init__(self, val, config):
        if val is None:
            val = self.DEFAULT_TOKEN_KEY
        self.key = val
        self.token = config.settings[val]

    def text(self):  # pragma: no cover
        return 'travis authoriztion token'

    phash = text

    def __call__(self, context, request):
        auth = request.headers.get('Authorization')
        slug = request.headers.get('Travis-Repo-Slug')

        if auth is None and slug is None:  # not for us.
            return False
        
        if auth is None or slug is None:   # bad protocol, no donut!
            raise HTTPForbidden()

        mashed = slug + self.token
        if isinstance(mashed, text_type):  # pragma: no cover
            mashed = mashed.encode('utf-8')

        if auth != sha256(mashed).hexdigest():  # wicked, evil, naughty!
            raise HTTPForbidden()

        return True


def generate_notification_mail(context, registry, payload, mailer=None):
    """Generate an e-mail to appropriate address

    ``context`` will be a ``Repo`` instance:  use it to derive the
    target address / formatter (e.g., if repo's __parent__ name
    is "zopefoundation", send mail to`zope-tests@zope.org``).

    ``payload`` is a mapping, as described here:
      http://docs.travis-ci.com/user/notifications/#Webhooks-Delivery-Format

    For ZF repos, mail should be formatted following the rules laid down
    here: http://docs.zope.org/zopetoolkit/process/buildbots.html
            #informing-the-zope-developer-community-about-build-results
    """


@view_config(context=Root, renderer='json',
             request_method="POST",
             header="Content-Type: application/x-www-form-urlencoded",
             travis_auth_check=None,  # use default key
            )
def webhook(context, request,
            generator=generate_notification_mail,  # testing hook
           ):
    """Process the notification POST from Travis:

    - Crack the `payload` from the form data and decode as JSON.

    - Use the slug to find / create the appendonly log based on the repo;
      store the deocded JSON in the log.

    - Delegate mail delivery to ``generator``.
    """
    owner_name, repo_name = request.headers['Travis-Repo-Slug'].split('/')
    owner = context.find_create(owner_name)
    repo = owner.find_create(repo_name)
    payload = loads(request.POST['payload'])
    repo.pushItem(payload)
    generator(request.registry, owner_name, repo_name, payload)


def get_main_template(request):
    main_template = get_renderer('templates/main.pt')
    return main_template.implementation()


@view_config(context=Root, renderer='templates/homepage.pt')
def home_page(context, request):
    return {'owners': sorted(context.keys())}


@view_config(context=Owner, renderer='templates/owner.pt')
def owner(context, request):
    return {'name': context.__name__, 'repos': sorted(context.keys())}


@view_config(context=Repo, renderer='templates/repo.pt')
def repo(context, request):
    return {'name': context.__name__, 'recent': list(context.recent)}


def includeme(config):
    config.add_view_predicate('travis_auth_check', TravisAuthorizationCheck)
    config.add_request_method(callable=get_main_template,
                              name='main_template',
                              property=True,
                              reify=True,
                             )
