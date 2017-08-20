#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


from __future__ import absolute_import
from serial.tools import list_ports

def _dump_port(logger, d):
    logger.info(u'{}:'.format(d.device))
    logger.info(u'  hwid        : "{}"'.format(d.hwid))
    logger.info(u'  manufacturer: "{}"'.format(d.manufacturer))
    logger.info(u'  product     : "{}"'.format(d.product))
    logger.info(u'  description : "{}"'.format(d.description))

def _dump_ports(logger):
    for d in list_ports.comports():
        _dump_port(logger, d)

def select_port(logger = None, dev_port = None, filters = None, must_unique = False):
    
    if filters != None and dev_port == None:
        not_unique = False
        for d in list_ports.comports():
            is_match = True
            for k, v in filters.items():
                if not hasattr(d, k):
                    continue
                a = getattr(d, k)
                if not a:
                    a = u''
                if not a.startswith(v):
                    is_match = False
            if is_match:
                if dev_port == None:
                    dev_port = d.device
                    if logger:
                        logger.info(u'choose device: ' + dev_port)
                        _dump_port(logger, d)
                else:
                    if logger:
                        logger.warning(u'find more than one port')
                    not_unique = True
        if not_unique:
            if logger:
                logger.info(u'current filter: {}, all ports:'.format(filters))
                _dump_ports(logger)
            if must_unique:
                raise Exception(u'port is not unique')
    
    if not dev_port:
        if logger:
            if filters:
                logger.error(u'port not found, current filter: {}, all ports:'.format(filters))
            else:
                logger.error(u'please specify dev_port or filters, all ports:')
            _dump_ports(logger)
        return None
    
    return dev_port

