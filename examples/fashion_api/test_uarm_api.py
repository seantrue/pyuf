#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


from __future__ import absolute_import
import sys, os
from time import sleep

sys.path.append(os.path.join(os.path.dirname(__file__), u'../..'))

from uf.wrapper.uarm_api import UarmAPI
from uf.utils.log import *

#logger_init(logging.VERBOSE)
#logger_init(logging.DEBUG)
logger_init(logging.INFO)

print u'setup uarm ...'

#uarm = UarmAPI(dev_port = '/dev/ttyUSB0')
#uarm = UarmAPI(filters = {'hwid': 'USB VID:PID=0403:6001'})
uarm = UarmAPI() # default by filters: {'hwid': 'USB VID:PID=0403:6001'}


print u'sleep 2 sec ...'
sleep(2)

print u'device info: '
print uarm.get_device_info()

print u'\nset X340 ...'
uarm.set_position(340, 0, 150)
print u'set X320 ...'
uarm.set_position(320, 0, 150)
print u'set X300 ...'
uarm.set_position(300, 0, 150)
print u'set X200 ...'
uarm.set_position(200, 0, 150)
print u'set X190 ...'
uarm.set_position(190, 0, 150)

# wait all async cmd return before send sync cmd
uarm.flush_cmd()

print u'set Z100 ...'
uarm.set_position(190, 0, 100, wait = True)
print u'set Z150 ...'
uarm.set_position(190, 0, 150, wait = True)

uarm.set_buzzer()

print u'done ...'
while True:
    sleep(1)

