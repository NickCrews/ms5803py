from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='ms5803py',
      version='0.1.4',
      description='Python library for MS5803-14BA pressure sensor for Raspberry Pi',
      long_description=long_description,
      long_description_content_type='text/markdown',
      copyright = 'Copyright (c) 2018 Nick Crews',
      url='https://github.com/NickCrews/ms5803py',
      author='Nick Crews',
      author_email='nicholas.b.crews@gmail.com',
      license='MIT',
      packages=['ms5803py'],
      zip_safe=False,
      keywords = [],
      classifiers = [
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        ])
