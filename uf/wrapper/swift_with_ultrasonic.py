#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


from __future__ import absolute_import
from time import sleep
from .swift_api import SwiftAPI
from ..swift.grove.ultrasonic import Ultrasonic
from ..utils.log import *


class SwiftWithUltrasonic(SwiftAPI):
    u'''
    The API wrapper of swift and swift_pro
    default kwargs: dev_port = None, baud = 115200, filters = {'hwid': 'USB VID:PID=2341:0042'}
                    ultrasonic_port = 'D8'
    '''
    def __init__(self, **kwargs):
        u'''
        '''
        
        super(SwiftWithUltrasonic, self).__init__(**kwargs)
        
        # init ultrasonic node:
        
        ultrasonic_iomap = {
            u'service':      u'ultrasonic',
            u'distance':     u'ultrasonic_report',
            u'cmd_sync':     u'ptc_sync',
            u'report':   u'ptc_report'
        }
        
        if u'ultrasonic_port' not in kwargs:
            kwargs[u'ultrasonic_port'] = u'D8'
        self._nodes[u'ultrasonic'] = Ultrasonic(self._ufc, u'ultrasonic', ultrasonic_iomap, port = kwargs[u'ultrasonic_port'])
        
        # init ultrasonic_api node:
        
        self._ultrasonic_ports = {
            u'ultrasonic':        {u'dir': u'out', u'type': u'service'},
            u'ultrasonic_report': {u'dir': u'in', u'type': u'topic', u'callback': self._ultrasonic_cb}
        }
        
        self._ultrasonic_iomap = {
            u'ultrasonic':        u'ultrasonic',
            u'ultrasonic_report': u'ultrasonic_report'
        }
        
        self.ultrasonic_cb = None
        
        self._ultrasonic_node = u'ultrasonic_api'
        self._ultrasonic_logger = logging.getLogger(self._ultrasonic_node)
        self._ufc.node_init(self._ultrasonic_node, self._ultrasonic_ports, self._ultrasonic_iomap)
    
    
    def _ultrasonic_cb(self, msg):
        if self.ultrasonic_cb != None:
            self.ultrasonic_cb(int(msg))
    
    def set_report_ultrasonic(self, interval):
        u'''
        Report distance from ultrasonic in (interval) microsecond.
        
        Args:
            interval: seconds, if 0 disable report
        
        Returns:
            None
        '''
        cmd = u'set report_distance on {}'.format(round(interval, 2))
        ret = self._ultrasonic_ports[u'ultrasonic'][u'handle'].call(cmd)
        if ret.startswith(u'ok'):
            return
        self._logger.error(u'set_report_ultrasonic ret: %s' % ret)
    
    def register_ultrasonic_callback(self, callback = None):
        u'''
        Set function to receiving current distance from ultrasonic sensor.
        Unit: cm
        
        Args:
            callback: set the callback function, undo by setting to None
        
        Returns:
            None
        '''
        self.ultrasonic_cb = callback
    
    def get_ultrasonic(self):
        u'''
        Get current distance from ultrasonic sensor
        
        Returns:
            int value of distance, unit: cm
        '''
        ret = self._ultrasonic_ports[u'ultrasonic'][u'handle'].call(u'get value')
        
        if ret.startswith(u'ok, '):
            return int(ret[4:])
        self._ultrasonic_logger.error(u'get value ret: %s' % ret)
        return None

