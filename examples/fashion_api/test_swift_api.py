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

from uf.wrapper.swift_api import SwiftAPI
from uf.utils.log import *

#logger_init(logging.VERBOSE)
#logger_init(logging.DEBUG)
logger_init(logging.INFO)

print u'setup swift ...'

#swift = SwiftAPI(dev_port = '/dev/ttyACM0')
#swift = SwiftAPI(filters = {'hwid': 'USB VID:PID=2341:0042'})
swift = SwiftAPI() # default by filters: {'hwid': 'USB VID:PID=2341:0042'}


print u'sleep 2 sec ...'
sleep(2)

print u'device info: '
print swift.get_device_info()

print u'\nset X350 Y0 Z50 F1500 ...'
# for the non-pro swift by current firmware,
# you have to specify all arguments for x, y, z and the speed
swift.set_position(350, 0, 50, speed = 1500)

print u'set X340 ...'
swift.set_position(x = 340)
print u'set X320 ...'
swift.set_position(x = 320)
print u'set X300 ...'
swift.set_position(x = 300)
print u'set X200 ...'
swift.set_position(x = 200)
print u'set X190 ...'
swift.set_position(x = 190)

# wait all async cmd return before send sync cmd
swift.flush_cmd()

print u'set Z100 ...'
swift.set_position(z = 100, wait = True)
print u'set Z150 ...'
swift.set_position(z = 150, wait = True)

swift.set_buzzer()

print u'done ...'
while True:
    sleep(1)

