from distutils.core import setup

setup(
    name='Zibrato',
    version='0.1.0',
    author='Rob Martin @version2beta',
    author_email='rob.martin@tartansolutions.com',
    packages=['zibrato'],
    scripts=[],
    url='http://pypi.python.org/pypi/zibrato/',
    license='LICENSE.txt',
    description='Send metrics to Librato via ZeroMQ.',
    long_description=open('README.txt').read(),
    install_requires=[
        'pyzmq',
    ],
)
