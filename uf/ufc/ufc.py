#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


class UFC(object):
    u'''\
    Communication wrapper for uFactory
    
    On the top of mediums:
      inner-thread-communication (only this availiable currently)
      ROS
      ACH IPC
      ZeroMQ
      etc...
    
    This wrapper support two communication type: Topic and Service,
    unlike the ROS Topic, if any of the subscriber's queue is full and the allow_drop flag is False,
    the publisher will block.
    
    All messages are raw data, using ascii string mostly, it could be raw binary data (or mixed) also.
    '''
    
    def node_init(self, node, ports, iomap):
        u'''\
        Format example for ports and iomap:
        
        ports = {
            'in': {'dir': 'in', 'type': 'topic', 'callback': self.io_in_cb, 'queue_size': 20},
            'out': {'dir': 'out', 'type': 'topic'},
            'service': {'dir': 'in', 'type': 'service', 'callback': self.io_service_cb}
        }
        
        iomap = {
            'out': 'PATH/TO/WIRE1',
            'service': 'PATH/TO/WIRE2'
        }
        '''
        
        for k, item in ports.items():
            item[u'handle'] = None
        
        for k, path in iomap.items():
            if ports[k][u'type'] == u'topic':
                if ports[k][u'dir'] == u'in':
                    kwargs = {}
                    if u'queue_size' in ports[k]:
                        kwargs[u'queue_size'] = ports[k][u'queue_size']
                    if u'allow_drop' in ports[k]:
                        kwargs[u'allow_drop'] = ports[k][u'allow_drop']
                    ports[k][u'handle'] = self.topic_subscriber(node, path, ports[k][u'callback'], **kwargs)
                elif ports[k][u'dir'] == u'out':
                    ports[k][u'handle'] = self.topic_publisher(node, path)
            elif ports[k][u'type'] == u'service':
                if ports[k][u'dir'] == u'in':
                    ports[k][u'handle'] = self.service_register(node, path, ports[k][u'callback'])
                elif ports[k][u'dir'] == u'out':
                    ports[k][u'handle'] = self.service_proxy(node, path)


