from distutils.core import setup

def readme():
    try:
        with open('README_short.rst', 'r') as f:
            return f.read()
    except:
        return ''

setup(
    name = 'fxcmpy',
    packages = ['fxcmpy'], # this must be the same as the name above
    version = '1.1.0',
    description = 'A Python Wrapper Class for the RESTful API as provided by FXCM Forex Capital Markets Ltd.',
    long_description = readme(),
    author = 'The Python Quants GmbH',
    author_email = 'admin@tpq.io',
    license='BSD',
    url = 'https://github.com/fxcm/fxcmpy', 
    download_url = 'https://github.com/fxcm/fxcmpy/archive/0.1.tar.gz', 
    keywords = 'FXCM API Python Wrapper Finance Algo Trading',
    install_requires=['pandas', 'socketIO_client', 'configparser', 'requests'], 
    classifiers = [],
)
