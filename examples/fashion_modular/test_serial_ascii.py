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
from uf.comm.serial_ascii import SerialAscii
from uf.utils.log import *

logger_init(logging.VERBOSE)

print u'setup ser_ascii ...'

ser_iomap = {
        u'out':     u'ser_out',
        u'in':      u'ser_in',
        u'service': u'ser_service'
}

ufc = ufc_init()
ser_ascii = SerialAscii(ufc, u'ser_ascii', ser_iomap, filters = {u'hwid': u'USB VID:PID=2341:0042'})


print u'setup test ...'
logger = logging.getLogger(u'test')

def ser_out_cb(msg):
    logger.debug(u'callback: ' + msg)

test_ports = {
        u'ser_out':     {u'dir': u'in',  u'type': u'topic', u'callback': ser_out_cb},
        u'ser_in':      {u'dir': u'out', u'type': u'topic'},
        u'ser_service': {u'dir': u'out', u'type': u'service'}
}

test_iomap = {
        u'ser_out':     u'ser_out',
        u'ser_in':      u'ser_in',
        u'ser_service': u'ser_service'
}

ufc.node_init(u'test', test_ports, test_iomap)


print u'\nsleep 2 sec ...\n'
sleep(2)

print u'\nset X330 ...'
test_ports[u'ser_in'][u'handle'].publish(u'G0 X300 Y0 Z50')

print u'test service ...'
print u'service ret: ' + test_ports[u'ser_service'][u'handle'].call(u'test string...')

print u'done ...'
while True:
    sleep(1)

