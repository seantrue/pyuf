#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


from __future__ import absolute_import
import logging

logging.VERBOSE = 5

def logger_init(level = logging.INFO):
    logging.basicConfig(format = u'%(levelname)s: %(name)s: %(message)s', level = level)
    logging.addLevelName(logging.VERBOSE, u'VERBOSE')


