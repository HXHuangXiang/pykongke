#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='pykongke',
    version='3.0.0',
    keywords=['konke', 'iot'],
    description='Python library for interfacing with konke smart appliances',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='HXHuangXiang',
    author_email='',
    url='https://github.com/HXHuangXiang/pykongke',
    license='GPLv3',
    install_requires=[
        'pycryptodome>=3.6.0'
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-asyncio',
        ],
    },
    packages=find_packages(include=['pykongke', 'pykongke.*']),
    include_package_data=True,
    python_requires='>=3.7',
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'pykongke = pykongke.__main__:main',
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
