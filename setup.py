from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='ms5803py',
      version='0.1.3',
      description='Python library for MS5803-14BA pressure sensor for Raspberry Pi',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/NickCrews/ms5803py',
      author='Nick Crews',
      author_email='nicholas.b.crews@gmail.com',
      license='MIT',
      packages=['ms5803py'],
      zip_safe=False)
