from setuptools import setup

setup(name='MS5803py',
      version='0.1',
      description='Python library for MS5803-14BA pressure sensor for Raspberry Pi',
      url='https://github.com/NickCrews/MS5803py',
      author='Nick Crews',
      author_email='nicholas.b.crews@gmail.com',
      license='MIT',
      packages=['MS5803-14BA-python'],
      install_requires=["smbus"],
      zip_safe=False)
