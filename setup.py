from setuptools import setup, find_packages
from codecs import open
from os import path
import platform

here = path.abspath(path.dirname(__file__))

# get requirements
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().splitlines()

# description for pypi
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    desc = f.read()

hand_reqs = ['hidapi', 'pyusb']
serial_reqs = ['pyserial']
key_mouse_reqs = ['pynput']
force_reqs = ['nidaqmx;platform_system=="Windows"']
demo_reqs = ['pynput', 'matplotlib', 'pyqtgraph']
full_reqs = hand_reqs + serial_reqs + key_mouse_reqs + force_reqs + demo_reqs
full_reqs = list(set(full_reqs))

setup(
    name='toon',
    version='0.12.6',
    description='Tools for neuroscience experiments',
    long_description=desc,
    long_description_content_type='text/markdown',
    url='https://github.com/aforren1/toon',
    author='Alexander Forrence',
    author_email='aforren1@jhu.edu',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    install_requires=requirements,
    extras_require={
        'full': full_reqs,
        'demo': demo_reqs,
        'hand': hand_reqs,
        'birds': serial_reqs,
        'key_mouse': key_mouse_reqs,
        'cyberglove': serial_reqs,
        'force': force_reqs
    },
    keywords='psychophysics neuroscience input experiment',
    packages=find_packages(exclude=['contrib', 'docs', 'tests'])
)
