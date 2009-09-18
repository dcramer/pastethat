import os
from setuptools import setup, find_packages

import pastethat

setup(name='Pastethat',
    version='.'.join(map(str, pastethat.__version__)),
    description='Source code for Pastethat.com',
    author='David Cramer',
    author_email='dcramer@gmail.com',
    url='http://github.com/dcramer/pastethat',
    packages=find_packages(),
    install_requires=[
        'Jinja2',
        'Coffin>=0.3',
        'django>=1.0',
    ],
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)
