from distutils.core import setup
from zibrato import __version__

setup(
    name='Zibrato',
    version=__version__,
    author='Rob Martin @version2beta',
    author_email='rob@version2beta.com',
    packages=['zibrato', 'zibrato.tests'],
    scripts=[],
    url='http://pypi.python.org/pypi/zibrato/',
    license='LICENSE.txt',
    description='Send metrics to Librato via ZeroMQ.',
    long_description=open('README.rst').read(),
    install_requires=[
        'pyzmq',
        'fuzzywuzzy',
        'requests',
        'simplejson',
    ],
    package_data={
        '': ['*.dist'],
    },
    entry_points = {
      'console_scripts': [
        'zibrato-broker = zibrato.backend:main',
        'zibrato-librato = zibrato.librato:main',
      ]
    }
)
