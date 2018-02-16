"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
import os

version_format = "{tag}.dev-{commitcount}-{gitsha}"
if os.environ.get('SETUPTOOLS_STAGE') == 'production':
    version_format = "{tag}"
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='rime',
    version_format=version_format,
    version="3.0",
    setup_requires=['setuptools-git-version'],
    description='A poorly-architected event dispatcher that does magic and lets you do terrible things',  # Required
    long_description=long_description,  # Optional
    url='https://github.com/zoidbb/rime',  # Optional
    author='Ber Zoidberg',  # Optional
    author_email='ber@zoidplex.net',  # Optional
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.3'
    ],
    packages=['rime','rime.core'],
    package_data={
        "rime": ["skel/*", "skel/content/*", "skel/data/*"]
        },
    entry_points={
    'console_scripts': [
            'rime = rime.cli:main',
        ],
    }
)

