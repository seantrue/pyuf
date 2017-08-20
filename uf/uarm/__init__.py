#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

from __future__ import absolute_import
from ..utils.module_group import ModuleGroup
from ..comm.serial_ascii import SerialAscii
from ..comm.protocol_ascii import ProtocolAscii
from .uarm_body import UarmBody
from .gripper import Gripper
from .pump import Pump

class Uarm(ModuleGroup):
    u'''\
    The top module of uArm Metal
    default kwargs: dev_port = None, baud = 115200, filters = {'hwid': 'USB VID:PID=0403:6001'}
    '''
    sub_nodes = [
        {
            u'module': SerialAscii,
            u'node': u'serial_ascii',
            u'args': [u'dev_port', u'baud', u'filters'],
            u'iomap': {
                u'out': u'inner: pkt_ser2ptc',
                u'in':  u'inner: pkt_ptc2ser'
            }
        },
        {
            u'module': ProtocolAscii,
            u'node': u'ptc_ascii',
            u'args': [u'cmd_pend_size'],
            u'iomap': {
                u'cmd_async':  u'outer: ptc_async',
                u'cmd_sync':   u'outer: ptc_sync',
                u'report':     u'outer: ptc_report',
                u'service':    u'outer: ptc',
                
                u'packet_in':  u'inner: pkt_ser2ptc',
                u'packet_out': u'inner: pkt_ptc2ser'
            }
        },
        {
            u'module': UarmBody,
            u'node': u'uarm_body',
            u'iomap': {
                u'pos_in':    u'outer: pos_in',
                u'pos_out':   u'outer: pos_out',
                u'buzzer':    u'outer: buzzer',
                u'service':   u'outer: service',
                
                u'cmd_async': u'outer: ptc_async',
                u'cmd_sync':  u'outer: ptc_sync',
                u'report':    u'outer: ptc_report'
            }
        },
        {
            u'module': Gripper,
            u'node': u'gripper',
            u'iomap': {
                u'service':  u'outer: gripper',
                u'cmd_sync': u'outer: ptc_sync'
            }
        },
        {
            u'module': Pump,
            u'node': u'pump',
            u'iomap': {
                u'service':      u'outer: pump',
                u'limit_switch': u'outer: limit_switch',
                u'cmd_sync':     u'outer: ptc_sync',
                u'report':       u'outer: ptc_report'
            }
        }
    ]
    
    def __init__(self, ufc, node, iomap, **kwargs):
        if u'dev_port' not in kwargs:
            kwargs[u'dev_port'] = None
        if u'baud' not in kwargs:
            kwargs[u'baud'] = 115200
        if u'filters' not in kwargs:
            kwargs[u'filters'] = {u'hwid': u'USB VID:PID=0403:6001'}
        if u'cmd_pend_size' not in kwargs:
            kwargs[u'cmd_pend_size'] = 1
        super(Uarm, self).__init__(ufc, node, iomap, **kwargs)


