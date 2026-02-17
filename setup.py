#!/usr/bin/env python3
"""
Setup configuration for ANIMAtiZE Framework
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
def read_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

requirements = read_requirements('requirements.txt')
cv_requirements = read_requirements('requirements-cv.txt')

setup(
    name='animatize-framework',
    version='1.0.0',
    description='Transform static images into cinematic masterpieces with AI-powered movement prediction',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='ANIMAtiZE Team',
    author_email='support@animatize.dev',
    url='https://github.com/makaronz/animatize',
    project_urls={
        'Documentation': 'https://docs.animatize.dev',
        'Source': 'https://github.com/makaronz/animatize',
        'Bug Tracker': 'https://github.com/makaronz/animatize/issues',
    },
    packages=find_packages(include=['src', 'src.*']),
    package_dir={'': '.'},
    include_package_data=True,
    package_data={
        'src': [
            'configs/*.json',
            'configs/*.yaml',
            'configs/*.yml',
        ],
    },
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require={
        'cv': cv_requirements,
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=1.0.0',
            'pre-commit>=3.0.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
            'sphinx-autodoc-typehints>=1.19.0',
        ],
        'monitoring': [
            'prometheus-client>=0.16.0',
            'opentelemetry-api>=1.15.0',
            'opentelemetry-sdk>=1.15.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'animatize=src.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Multimedia :: Video',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Image Recognition',
    ],
    keywords='ai, computer-vision, video-generation, cinematic, image-processing, deep-learning',
    license='MIT',
    zip_safe=False,
)
