from distutils.core import setup
setup(
    name = 'fxcmpy',
    packages = ['fxcm'], # this must be the same as the name above
    version = '0.5.4',
    description = 'A Python Wrapper Class for the RESTful API as provided by FXCM Forex Capital Markets Ltd.',
    author = 'The Python Quants GmbH',
    author_email = 'admin@tpq.io',
    url = 'https://mschwed@bitbucket.org/mschwed/fxcmpy.git', 
    download_url = 'https://mschwed@bitbucket.org/mschwed/fxcmpy/archive/0.1.tar.gz', # I'll explain this in a second
    keywords = ['FXCM', 'API', 'Python', 'Wrapper'], # arbitrary keywords
    install_requires=['pandas', 'socketIO_client', 'configparser', 'requests'], 
    classifiers = [],
)
