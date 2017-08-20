#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>

from __future__ import absolute_import
from time import sleep
from ..utils.log import *


class Keys(object):
    def __init__(self, ufc, node, iomap):
        
        self.ports = {
            u'service': {u'dir': u'in', u'type': u'service', u'callback': self.service_cb},
            u'key0': {u'dir': u'out', u'type': u'topic'},
            u'key1': {u'dir': u'out', u'type': u'topic'},
            
            u'cmd_sync': {u'dir': u'out', u'type': u'service'},
            u'report': {u'dir': u'in', u'type': u'topic', u'callback': self.report_cb}
        }
        
        self.logger = logging.getLogger(node)
        ufc.node_init(node, self.ports, iomap)
    
    def report_cb(self, msg):
        if self.ports[u'key0'][u'handle']:
            if msg == u'4 B0 V1':
                self.ports[u'key0'][u'handle'].publish(u'short press')
            elif msg == u'4 B0 V2':
                self.ports[u'key0'][u'handle'].publish(u'long press')
        if self.ports[u'key1'][u'handle']:
            if msg == u'4 B1 V1':
                self.ports[u'key1'][u'handle'].publish(u'short press')
            elif msg == u'4 B1 V2':
                self.ports[u'key1'][u'handle'].publish(u'long press')
    
    def service_cb(self, msg):
        words = msg.split(u' ', 1)
        action = words[0]
        
        words = words[1].split(u' ', 1)
        param = words[0]
        
        if param == u'key_owner':
            if action == u'get':
                return u'err, get not support'
            
            if action == u'set':
                self.logger.debug(u'set value: %s' % words[1])
                if words[1] == u'default':
                    return self.ports[u'cmd_sync'][u'handle'].call(u'P2213 V1')
                elif words[1] == u'user':
                    return self.ports[u'cmd_sync'][u'handle'].call(u'P2213 V0')
                return u'err, value not support'

