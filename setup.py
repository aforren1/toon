from setuptools import setup, find_packages
from setuptools.extension import Extension
from os import path
from Cython.Build import cythonize
from sys import platform
import numpy as np

cxxflags = []
ldflags = []
if platform == 'win32':
    cxxflags.append('/std:c++14')
elif platform == 'darwin':
    cxxflags.extend(['-std=c++11', '-stdlib=libc++'])
else:
    cxxflags.append('-std=c++11')

ext = [Extension('toon.util.clock', ['toon/util/clock.pyx'], 
                 language='c++', extra_compile_args=cxxflags)]


defs = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
ext.extend([
    Extension('toon.anim.easing', sources=['toon/anim/easing.pyx']),
    Extension('toon.anim.interpolators', sources=['toon/anim/interpolators.pyx']),
    Extension('toon.anim.track', sources=['toon/anim/track.pyx'], include_dirs=[np.get_include()],
              define_macros=defs),
    Extension('toon.anim.player', sources=['toon/anim/player.pyx'])
])

here = path.abspath(path.dirname(__file__))

# get requirements
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().splitlines()

# description for pypi
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    desc = f.read()

setup(
    name='toon',
    version='0.15.2a1',
    description='Tools for neuroscience experiments',
    long_description=desc,
    long_description_content_type='text/markdown',
    url='https://github.com/aforren1/toon',
    author='Alexander Forrence',
    author_email='alex.forrence@gmail.com',
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
