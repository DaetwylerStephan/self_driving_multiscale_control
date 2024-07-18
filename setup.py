from setuptools import setup

from setuptools import setup

import os
import re

HERE = os.path.abspath(os.path.dirname(__file__))

exc_folders = ['__pycache__', '__init__.py']
subpkgs = os.listdir(os.path.join(HERE,'multiScale'))
subpkgs = [pkg for pkg in subpkgs if pkg not in exc_folders]
print(subpkgs)

with open("requirements.txt", "r") as fp:
    install_requires = list(fp.read().splitlines())

setup(name='multiScaleAnalysis',
	  version='0.1.0',
	  description='Analysis and Visualization of multi-scale light-sheet data',
	  author='Stephan Daetwyler, Reto Fiolka',
	  packages=['multiScale'] + ['multiScale.'+ pkg for pkg in subpkgs] + ['multiScale.SegmentationHighres.gradient_watershed'],
	  include_package_data=True,
	  install_requires=install_requires,
)







