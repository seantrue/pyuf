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

from uf.ufc import ufc_init
from uf.swift import Swift
from uf.utils.log import *

logger_init(logging.DEBUG)

print u'setup swift ...'

swift_iomap = {
        u'pos_in':  u'swift_pos_in',
        u'service': u'swift_service',
        u'gripper': u'swift_gripper'
}

ufc = ufc_init()
swift = Swift(ufc, u'swift', swift_iomap)


print u'setup test ...'

test_ports = {
        u'swift_pos':     {u'dir': u'out', u'type': u'topic'},
        u'swift_service': {u'dir': u'out', u'type': u'service'},
        u'swift_gripper': {u'dir': u'out', u'type': u'service'}
}

test_iomap = {
        u'swift_pos':     u'swift_pos_in',
        u'swift_service': u'swift_service',
        u'swift_gripper': u'swift_gripper'
}

# install handle for ports which are listed in the iomap
ufc.node_init(u'test', test_ports, test_iomap)


print u'sleep 2 sec ...'
sleep(2)


print u'set X190: ' + test_ports[u'swift_service'][u'handle'].call(u'set cmd_sync G0 X190 Z50')

# FIXME: 'set on' always timeout according to firmware's bug
print u'gripper set on return: ' + test_ports[u'swift_gripper'][u'handle'].call(u'set value on')
print u'gripper get state return: ' + test_ports[u'swift_gripper'][u'handle'].call(u'get value')

print u'gripper set off return: ' + test_ports[u'swift_gripper'][u'handle'].call(u'set value off')
print u'gripper get state return: ' + test_ports[u'swift_gripper'][u'handle'].call(u'get value')

print u'done ...'
while True:
    sleep(1)

