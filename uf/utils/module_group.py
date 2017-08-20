#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, UFactory, Inc.
# All rights reserved.
#
# Author: Duke Fong <duke@ufactory.cc>


class ModuleGroup(object):
    def __init__(self, ufc, node, iomap, **kwargs):
        self.nodes = {}
        for n in self.__class__.sub_nodes:
            args = {}
            if u'args' in n.keys():
                for k in n[u'args']:
                    args[k] = kwargs[k]
            for io in list(n[u'iomap']):
                t, p = n[u'iomap'][io].split(u': ', 1)
                if t == u'outer':
                    if p in iomap.keys():
                        n[u'iomap'][io] = iomap[p]
                    else:
                        # del n['iomap'][io]
                        # don't delete, may used by internal
                        n[u'iomap'][io] = node + u'/' + p
                elif t == u'inner':
                    n[u'iomap'][io] = node + u'/' + p
            self.nodes[n[u'node']] = n[u'module'](ufc, node + u'/' + n[u'node'], n[u'iomap'], **args)


