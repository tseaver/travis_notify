import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()

requires = [
    'appendonly>=1.2',
    'persistent',
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_mailer',
    'pyramid_tm',
    'pyramid_zodbconn',
    'repoze.folder',
    'transaction',
    'ZODB',
    'waitress',
    ]

setup(name='travis_notify',
      version='0.1.dev0',
      description='travis_notify',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="travis_notify",
      entry_points="""\
      [paste.app_factory]
      main = travis_notify:main
      [paste.filter_app_factory]
      translogger = travis_notify.translogger:make_filter
      """,
      )
