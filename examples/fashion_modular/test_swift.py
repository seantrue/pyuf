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
#logger_init(logging.DEBUG)
logger_init(logging.INFO)

print u'setup swift ...'

swift_iomap = {
        u'pos_in':  u'swift_pos_in',
        u'pos_out': u'swift_pos_out',
        u'service': u'swift_service'
}

ufc = ufc_init()
#swift = Swift(ufc, 'swift', swift_iomap, dev_port = '/dev/ttyACM0')
#swift = Swift(ufc, 'swift', swift_iomap, filters = {'hwid': 'USB VID:PID=2341:0042'})
swift = Swift(ufc, u'swift', swift_iomap) # default by filters: {'hwid': 'USB VID:PID=2341:0042'}


print u'setup test ...'

def pos_cb(msg):
    print u'pos_cb: ' + msg

test_ports = {
        u'swift_pos':     {u'dir': u'out', u'type': u'topic'},
        u'swift_pos_out': {u'dir': u'in',  u'type': u'topic', u'callback': pos_cb},
        u'swift_service': {u'dir': u'out', u'type': u'service'}
}

test_iomap = {
        u'swift_pos':     u'swift_pos_in',
        u'swift_pos_out': u'swift_pos_out',
        u'swift_service': u'swift_service'
}

# install handle for ports which are listed in the iomap
ufc.node_init(u'test', test_ports, test_iomap)


print u'sleep 2 sec ...'
sleep(2)


print u'enable report_pos: ' + test_ports[u'swift_service'][u'handle'].call(u'set report_pos on 0.2')
#print('disable report_pos: ' + test_ports['swift_service']['handle'].call('set report_pos off'))

print u'set X330 ...'
# topics are always async
# without 'G0', port 'pos' is dedicated for moving
test_ports[u'swift_pos'][u'handle'].publish(u'X350 Y0 Z50')


print u'ret1: ' + test_ports[u'swift_service'][u'handle'].call(u'set cmd_sync G0 X340')
print u'ret2: ' + test_ports[u'swift_service'][u'handle'].call(u'set cmd_sync G0 X320')
print u'ret3: ' + test_ports[u'swift_service'][u'handle'].call(u'set cmd_sync G0 X300')
print u'ret4: ' + test_ports[u'swift_service'][u'handle'].call(u'set cmd_sync G0 X200')
print u'ret5: ' + test_ports[u'swift_service'][u'handle'].call(u'set cmd_sync G0 X190')

print u'done ...'
while True:
    sleep(1)

