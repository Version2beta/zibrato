from distutils.core import setup

setup(
    name='Zibrato',
    version='0.1.7',
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
)
