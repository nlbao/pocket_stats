'''
  setup.py
'''

from os import path
from setuptools import setup


# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pocket_stats',
    version='0.2.2',
    description='Tools for the Pocket reading app https://app.getpocket.com/',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nlbao/pocket_stats.git',
    author='Bao Nguyen',
    author_email='nlbao95@gmail.com',
    license='MIT',
    packages=['pocket_stats'],
    install_requires=[
        'setuptools',
        'click',
        'pocket-api',
        'dash',
        'dash-renderer',
        'dash-html-components',
        'dash-core-components',
        'plotly',
        'nltk',
        'tldextract',
        'pandas',
    ],
    tests_require=['pytest', 'pytest-cov', 'freezegun'],
    zip_safe=False
)
