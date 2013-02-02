#!/usr/bin/env python
import os
import re
from setuptools import setup


version = None
for line in open('./noodleamp/__init__.py'):
    m = re.search('__version__\s*=\s*(.*)', line)
    if m:
        version = m.group(1).strip()[1:-1]  # quotes
        break
assert version


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='noodleamp',
    version=version,
    author='Michael Kelly',
    author_email='me@mkelly.me',
    description='It plays the musaks.',
    license='MIT',
    keywords='noodle music musaks sound gstreamer noodleamp',
    url='https://github.com/nooodle/noodleamp',
    packages=['noodleamp'],
    long_description=read('README.md'),
    entry_points={
        'console_scripts': [
            'noodleamp = noodleamp.cmd:main'
        ]
    }
)
