from travis_notify.models import Owner, Repo
import transaction


if __name__ == '__main__':

    try:
        zf = root['zopefoundation']
    except KeyError:
        zf = root['zopefoundation'] = Owner()

    for repo in (
        'zope.component',
        'zope.configuration',
        'zope.copy',
        'zope.deprecation',
        'zope.event',
        'zope.exceptions',
        'zope.hookable',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.location',
        'zope.proxy',
        'zope.schema',
        'zope.security',
        'zope.testing',
        'zope.testrunner',
        'zopetoolkit',
        ):
        if repo not in zf:
            zf[repo] = Repo()

    transaction.commit()
