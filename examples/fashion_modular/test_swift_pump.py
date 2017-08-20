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


#logger_init(logging.VERBOSE)
logger_init(logging.INFO)
ufc = ufc_init()


print u'setup swift ...'
swift_iomap = {
        u'pos_in':       u'swift_pos_in',
        u'service':      u'swift_service',
        u'pump':         u'swift_pump',
        u'limit_switch': u'limit_switch'
}
swift = Swift(ufc, u'swift', swift_iomap)


print u'setup test ...'

def limit_switch_cb(msg):
    print u'limit_switch state: ' + msg

test_ports = {
        u'swift_pos':     {u'dir': u'out', u'type': u'topic'},
        u'swift_service': {u'dir': u'out', u'type': u'service'},
        u'swift_pump':    {u'dir': u'out', u'type': u'service'},
        u'limit_switch':  {u'dir': u'in',  u'type': u'topic', u'callback': limit_switch_cb},
}
test_iomap = {
        u'swift_pos':     u'swift_pos_in',
        u'swift_service': u'swift_service',
        u'swift_pump':    u'swift_pump',
        u'limit_switch':  u'limit_switch'
}
# install handle for ports which are listed in the iomap
ufc.node_init(u'test', test_ports, test_iomap)


print u'sleep 2 sec ...'
sleep(2)

print u'get dev_info return: ' + test_ports[u'swift_service'][u'handle'].call(u'get dev_info')

# send arbitrary command
print u'set X190: ' + test_ports[u'swift_service'][u'handle'].call(u'set cmd_sync G0 X190 Z50')

# FIXME: 'set on' never timeout according to the firmware or hardware
print u'pump set on return: ' + test_ports[u'swift_pump'][u'handle'].call(u'set value on')
print u'pump get state return: ' + test_ports[u'swift_pump'][u'handle'].call(u'get value')

print u'pump set off return: ' + test_ports[u'swift_pump'][u'handle'].call(u'set value off')
print u'pump get state return: ' + test_ports[u'swift_pump'][u'handle'].call(u'get value')

print u'get limit_switch return: ' + test_ports[u'swift_pump'][u'handle'].call(u'get limit_switch')


print u'done ...'
while True:
    sleep(1)

