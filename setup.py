from setuptools import setup, find_packages


setup(name='pyeagle',
      version='0.1.1',
      description='Read/write EAGLE 6 CAD files',
      long_description=open('README.rst').read(),
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: OSI Approved :: MIT License',
      ],
      keywords='eagle pcb cadsoft schematic eda',
      url='http://github.com/storborg/pyeagle',
      author='Scott Torborg',
      author_email='storborg@gmail.com',
      install_requires=[
          'lxml',
      ],
      license='MIT',
      packages=find_packages(),
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
