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


class Pump(object):
    def __init__(self, ufc, node, iomap):
        
        self.ports = {
            u'service': {u'dir': u'in', u'type': u'service', u'callback': self.service_cb},
            u'limit_switch': {u'dir': u'out', u'type': u'topic'},
            
            u'cmd_sync': {u'dir': u'out', u'type': u'service'},
            u'report': {u'dir': u'in', u'type': u'topic', u'callback': self.report_cb}
        }
        
        self.logger = logging.getLogger(node)
        ufc.node_init(node, self.ports, iomap)
    
    def set_pump(self, val):
        if val == u'on':
            self.ports[u'cmd_sync'][u'handle'].call(u'M231 V1')
        else:
            self.ports[u'cmd_sync'][u'handle'].call(u'M231 V0')
        
        # TODO: modify the default timeout time with a service command
        for _ in xrange(20):
            ret = self.ports[u'cmd_sync'][u'handle'].call(u'P231')
            if val == u'on':
                if ret == u'OK V2': # grabbed
                    return u'ok'
            else:
                if ret == u'OK V0': # stop
                    return u'ok'
            sleep(0.5)
        return u'err, timeout for {}, last ret: {}'.format(val, ret)
    
    def report_cb(self, msg):
        if not self.ports[u'limit_switch'][u'handle']:
            return
        if msg == u'6 N0 V0':
            self.ports[u'limit_switch'][u'handle'].publish(u'off')
        elif msg == u'6 N0 V1':
            self.ports[u'limit_switch'][u'handle'].publish(u'on')
    
    def service_cb(self, msg):
        words = msg.split(u' ', 1)
        action = words[0]
        
        words = words[1].split(u' ', 1)
        param = words[0]
        
        if param == u'value':
            if action == u'get':
                ret = self.ports[u'cmd_sync'][u'handle'].call(u'P231')
                self.logger.debug(u'get value ret: %s' % ret)
                
                if ret == u'OK V0':
                    return u'ok, stoped'
                elif ret == u'OK V1':
                    return u'ok, working'
                elif ret == u'OK V2':
                    return u'ok, grabbed'
                else:
                    return u'err, unkown ret: %s' % ret
            
            if action == u'set':
                self.logger.debug(u'set value: %s' % words[1])
                return self.set_pump(words[1])
        
        elif param == u'limit_switch':
            if action == u'get':
                ret = self.ports[u'cmd_sync'][u'handle'].call(u'P233')
                self.logger.debug(u'get limit_switch ret: %s' % ret)
                
                if ret == u'OK V0':
                    return u'ok, off'
                elif ret == u'OK V1':
                    return u'ok, on'
                else:
                    return u'err, unkown ret: %s' % ret

