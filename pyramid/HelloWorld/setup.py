import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid==1.2',
    'pyramid_jinja2',
#    'repoze.tm2',
    'sqlalchemy==0.7.2',
    'zope.sqlalchemy',
#    'WebError',
    ]

setup(name='HelloWorld',
      version='0.1',
      description='HelloWorld',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="helloworld",
      entry_points = """\
      [paste.app_factory]
      app = helloworld:app
      """,
      paster_plugins=['pyramid'],
      )

