#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

from __future__ import absolute_import
from time import sleep
from ...utils.log import *


class Ultrasonic(object):
    def __init__(self, ufc, node, iomap, port = u'D8'):
        
        self.ports = {
            u'service': {u'dir': u'in', u'type': u'service', u'callback': self.service_cb},
            u'distance': {u'dir': u'out', u'type': u'topic'},
            
            u'cmd_sync': {u'dir': u'out', u'type': u'service'},
            u'report': {u'dir': u'in', u'type': u'topic', u'callback': self.report_cb}
        }
        
        self.distance = u'-1'
        self.port = port
        self.logger = logging.getLogger(node)
        ufc.node_init(node, self.ports, iomap)
    
    def report_cb(self, msg):
        if msg.startswith(u'10 N12 V'):
            self.distance = msg[8:]
            if self.ports[u'distance'][u'handle']:
                self.ports[u'distance'][u'handle'].publish(self.distance)
    
    def service_cb(self, msg):
        words = msg.split(u' ', 1)
        action = words[0]
        
        words = words[1].split(u' ', 1)
        param = words[0]
        
        if param == u'value':
            if action == u'get':
                return u'ok, ' + self.distance
            else:
                return u'err, action "{}" not allowed for value'.format(action)
        
        if param == u'report_distance':
            if action == u'set':
                if words[1] == u'off':
                    return self.ports[u'cmd_sync'][u'handle'].call(u'M2301 N12 V0')
                elif words[1].startswith(u'on '):
                    # init, choose port D8 or D9, the buggy firmware always return ok even set to a wrong port number
                    self.ports[u'cmd_sync'][u'handle'].call(u'M2300 N12 ' + self.port)
                    # unit: microsecond, format e.g.: set report_distance on 500
                    return self.ports[u'cmd_sync'][u'handle'].call(u'M2301 N12 V' + words[1][3:])

