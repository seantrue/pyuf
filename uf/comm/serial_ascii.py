#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


from __future__ import absolute_import
import threading
import serial
from serial.tools import list_ports
from ..utils.select_serial_port import select_port
from ..utils.log import *
from itertools import imap

class SerialAscii(threading.Thread):
    def __init__(self, ufc, node, iomap, dev_port = None, baud = 115200, filters = None):
        
        self.ports = {
            u'in': {u'dir': u'in', u'type': u'topic', u'callback': self.in_cb},
            u'out': {u'dir': u'out', u'type': u'topic'},
            u'service': {u'dir': u'in', u'type': u'service', u'callback': self.service_cb}
        }
        
        self.node = node
        self.logger = logging.getLogger(node)
        ufc.node_init(node, self.ports, iomap)
        
        dev_port = select_port(logger = self.logger, dev_port = dev_port, filters = filters)
        if not dev_port:
            quit(1)
        
        # TODO: maintain serial connection by service callback
        self.com = serial.Serial(port = dev_port, baudrate = baud)
        if not self.com.isOpen():
            raise Exception(u'serial open failed')
        threading.Thread.__init__(self)
        self.daemon = True
        self.alive = True
        self.start()
    
    def run(self):
        while self.alive:
            line = self.com.readline()
            if not line:
                continue
            line = u''.join(imap(unichr, line)).rstrip()
            if self.ports[u'out'][u'handle']:
                self.ports[u'out'][u'handle'].publish(line)
            self.logger.log(logging.VERBOSE, u'-> ' + line)
        self.com.close()
    
    def stop(self):
        self.alive = False
        self.join()
    
    def in_cb(self, message):
        self.com.write(str(imap(ord, message + u'\n')))
        self.logger.log(logging.VERBOSE, u'<- ' + message)
    
    def service_cb(self, message):
        pass


