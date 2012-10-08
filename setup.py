#-------------------------------------------------------------------------------
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Sean Ross-Ross
#
#-------------------------------------------------------------------------------

from setuptools import setup, find_packages

setup(name='traity',
      version='0.0.1',
      description='Extended Python Porperties',
      packages=find_packages(),
      author='Sean Ross-Ross',
      author_email='srossross@enthought.com',
      url='http://srossross.github.com/traity',
      classifiers=['Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3'],
      license='BSD',
      )

