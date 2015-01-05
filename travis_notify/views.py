from hashlib import sha256
from json import loads

from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import view_config

from .models import Root

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


@view_config(context=Root, renderer='templates/homepage.pt')
def home_page(context, request):
    return {'owners': list(context.keys())}



def generate_notification_mail(registry, owner_name, repo_name, payload):
    """Generate an e-mail to appropriate address

    Base address on ``owner_name`` / ``repo_name`` (e.g., if owner name
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
            mailer=generate_notification_mail,  # testing hook
           ):
    """Process the notification POST from Travis:

    - Crack the `payload` from the form data and decode as JSON.

    - Use the slug to find / create the appendonly log based on the repo;
      store the deocded JSON in the log.

    - Delegate mail delivery to ``mailer``.
    """
    owner_name, repo_name = request.headers['Travis-Repo-Slug'].split('/')
    owner = context.find_create(owner_name)
    repo = owner.find_create(repo_name)
    payload = loads(request.POST['payload'])
    repo.pushItem(payload)
    mailer(request.registry, owner_name, repo_name, payload)


def includeme(config):
    config.add_view_predicate('travis_auth_check', TravisAuthorizationCheck)
