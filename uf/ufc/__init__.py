#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

from __future__ import absolute_import
from .ufc_thread import UFCThread
from .ufc import UFC

def ufc_init(medium = u'thread'):
    if medium == u'thread':
        return UFCThread()
    else:
        raise Exception(u'medium not support')


