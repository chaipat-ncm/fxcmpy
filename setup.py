from distutils.core import setup
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'fxcmpy')
import VERSION

def readme():
    try:
        with open('README_short.rst', 'r') as f:
            return f.read()
    except:
        return ''

def read_version():
    file_name = os.path.join('fxcmpy', 'VERSION')
    with open(file_name, 'r') as f:
        ret = f.read()
    if ret[-1] == '\n':
        ret = ret[:-1]
    return ret

setup(
    name = 'fxcmpy',
    packages = ['fxcmpy'], # this must be the same as the name above
    version = VERSION.version,
    description = 'A Python Wrapper Class for the RESTful API as provided by FXCM Forex Capital Markets Ltd.',
    long_description = readme(),
    author = 'The Python Quants GmbH',
    author_email = 'admin@tpq.io',
    license='BSD',
    url = 'https://github.com/fxcm/fxcmpy', 
    download_url = 'https://github.com/fxcm/fxcmpy', 
    keywords = 'FXCM API Python Wrapper Finance Algo Trading',
    install_requires=['pandas', 'socketIO_client', 'configparser', 'requests'], 
    python_requires='>=3.4',
    classifiers = ['Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6']
)
