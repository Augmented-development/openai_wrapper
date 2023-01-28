#!/usr/bin/env python

from pathlib import Path

from setuptools import setup

setup(
    name='openai-wrapper',
    description='OOP wrapper and utils for OpenAI API',
    version='0.0.1',
    packages=['openai_wrapper'],
    author='Petr Lavrov',
    author_email='petr.b.lavrov@gmail.com',
    long_description=Path('README.md').read_text(),
    install_requires=Path('requirements.txt').read_text().split(),
    url='https://github.com/Augmented-development/openai_wrapper',
    py_modules=["openai_wrapper"],
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

)
