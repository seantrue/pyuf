#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


from __future__ import absolute_import
import _thread, threading
from Queue import Queue
from ..utils.log import *

csys_gstr = {
    u'polar': u'G201 ',
    u'cartesian': u'G0 '
}

class UarmBody(object):
    def __init__(self, ufc, node, iomap):
        
        self.ports = {
            u'pos_in': {u'dir': u'in', u'type': u'topic', u'callback': self.pos_in_cb},
            u'pos_out': {u'dir': u'out', u'type': u'topic'}, # report current position
            
            u'buzzer': {u'dir': u'in', u'type': u'topic', u'callback': self.buzzer_cb},
            
            #'status': {'dir': 'out', 'type': 'topic'}, # report unconnect, etc...
            u'service': {u'dir': u'in', u'type': u'service', u'callback': self.service_cb},
            
            u'cmd_async': {u'dir': u'out', u'type': u'topic'},
            u'cmd_sync': {u'dir': u'out', u'type': u'service'},
            u'report': {u'dir': u'in', u'type': u'topic', u'callback': self.report_cb}
        }
        
        self.logger = logging.getLogger(node)
        self.mode = u'play'
        self.coordinate_system = u'cartesian'
        
        ufc.node_init(node, self.ports, iomap)
    
    def buzzer_cb(self, msg):
        u'''msg format: "F1000 T0.2", F: frequency, T: time period (s)'''
        self.ports[u'cmd_async'][u'handle'].publish(u'M210 ' + msg)
    
    # TODO: create a thread to maintain device status and read dev_info
    def read_dev_info(self):
        info = []
        for c in xrange(201, 206):
            ret = u''
            while not ret.startswith(u'OK'):
                ret = self.ports[u'cmd_sync'][u'handle'].call(u'P%d' % c)
            info.append(ret.split(u' ', 1)[1])
        return u' '.join(info)
    
    def report_cb(self, msg):
        if msg[:2] == u'3 ' and self.ports[u'pos_out'][u'handle']:
            self.ports[u'pos_out'][u'handle'].publish(msg[2:])
    
    def pos_in_cb(self, msg):
        if self.ports[u'cmd_async'][u'handle']:
            cmd = csys_gstr[self.coordinate_system] + msg
            self.ports[u'cmd_async'][u'handle'].publish(cmd)
    
    def service_cb(self, msg):
        words = msg.split(u' ', 1)
        action = words[0]
        
        words = words[1].split(u' ', 1)
        param = words[0]
        
        if param == u'mode':
            if action == u'get':
                return u'ok, ' + self.mode
        
        if param == u'dev_info':
            if action == u'get':
                return u'ok, ' + self.read_dev_info()
        
        if param == u'coordinate_system':
            if action == u'get':
                return u'ok, ' + self.coordinate_system
            if action == u'set':
                self.logger.debug(u'coordinate_system: %s -> %s' % (self.coordinate_system, words[1]))
                self.coordinate_system = words[1]
                return u'ok'
        
        if param == u'report_pos':
            if action == u'set':
                if words[1] == u'off':
                    return self.ports[u'cmd_sync'][u'handle'].call(u'M120 V0')
                elif words[1].startswith(u'on '):
                    # unit: second, format e.g.: set report_pos on 0.2
                    return self.ports[u'cmd_sync'][u'handle'].call(u'M120 V' + words[1][3:])
        
        if param == u'cmd_sync':
            if action == u'set':
                return self.ports[u'cmd_sync'][u'handle'].call(words[1])
        
        if param == u'cmd_async':
            if action == u'set':
                self.ports[u'cmd_async'][u'handle'].publish(words[1])
                return u'ok'


