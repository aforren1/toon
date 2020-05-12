from setuptools import setup, find_packages
from setuptools.extension import Extension
from os import path
from Cython.Build import cythonize
from sys import platform

flags = []
if platform == 'win32':
    flags.append('/std:c++14')
else:
    flags.append('-std=c++11')

if platform == 'darwin':
    flags.append('-stdlib=libc++')

ext = [Extension('toon.util.clock', ['toon/util/clock.pyx'], 
                 language='c++', extra_compile_args=flags)]

here = path.abspath(path.dirname(__file__))

# get requirements
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().splitlines()

# description for pypi
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    desc = f.read()

setup(
    name='toon',
    version='0.15.0',
    description='Tools for neuroscience experiments',
    long_description=desc,
    long_description_content_type='text/markdown',
    url='https://github.com/aforren1/toon',
    author='Alexander Forrence',
    author_email='aforren1@jhu.edu',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
    install_requires=requirements,
    keywords='psychophysics neuroscience input experiment',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'example_devices']),
    ext_modules=cythonize(ext, language_level='3', annotate=True)
)
