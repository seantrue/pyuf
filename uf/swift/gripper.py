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


class Gripper(object):
    def __init__(self, ufc, node, iomap):
        
        self.ports = {
            u'service': {u'dir': u'in', u'type': u'service', u'callback': self.service_cb},
            
            u'cmd_sync': {u'dir': u'out', u'type': u'service'},
        }
        
        self.logger = logging.getLogger(node)
        ufc.node_init(node, self.ports, iomap)
    
    def set_gripper(self, val):
        if val == u'on':
            self.ports[u'cmd_sync'][u'handle'].call(u'M2232 V1')
        else:
            self.ports[u'cmd_sync'][u'handle'].call(u'M2232 V0')
        
        # TODO: modify the default timeout time with a service command
        for _ in xrange(20):
            ret = self.ports[u'cmd_sync'][u'handle'].call(u'P2232')
            if val == u'on':
                if ret == u'ok V2': # grabbed
                    return u'ok'
            else:
                if ret == u'ok V0': # stop
                    return u'ok'
            sleep(0.5)
        return u'err, timeout for {}, last ret: {}'.format(val, ret)
    
    def service_cb(self, msg):
        words = msg.split(u' ', 1)
        action = words[0]
        
        words = words[1].split(u' ', 1)
        param = words[0]
        
        if param == u'value':
            if action == u'get':
                ret = self.ports[u'cmd_sync'][u'handle'].call(u'P2232')
                self.logger.debug(u'get value ret: %s' % ret)
                
                if ret == u'ok V0':
                    return u'ok, stoped'
                elif ret == u'ok V1':
                    return u'ok, working'
                elif ret == u'ok V2':
                    return u'ok, grabbed'
                else:
                    return u'err, unkown ret: %s' % ret
            
            if action == u'set':
                self.logger.debug(u'set value: %s' % words[1])
                return self.set_gripper(words[1])


