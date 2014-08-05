#!/usr/bin/env python2
# -*- encoding: utf8 -*-

import sys
from ConfigParser import SafeConfigParser

class SnmpManager:
    def __init__(self):
        self.systems = {}

    def add_system(self, id_, desc, addr, port, comm_ro):
        self.systems[id_] = { \
            'description': desc, \
            'address': addr, \
            'port': int(port), \
            'community_ro': comm_ro, \
            'checks': {}, \
        }

    def add_check(self, id_, oid, desc, system):
        oid_tuple = tuple([int(i) for i in oid.split(':')])
        self.systems[system]['checks'][id_] = { \
            'description': desc, \
            'oid': oid_tuple, \
        }

def main(conf_file=""):
    if not conf_file:
        sys.exit(-1)
    config = SafeConfigParser()
    config.read(conf_file)
    snmp_manager = SnmpManager()
    for system in (s for s in config.sections() if s.startswith('system')):
        snmp_manager.add_system(system, \
                                config.get(system, 'description'), \
                                config.get(system, 'address'), \
                                config.get(system, 'port'), \
                                config.get(system, 'communityro'))
    for check in (c for c in config.sections() if c.startswith('check')):
        snmp_manager.add_check(check, \
                               config.get(check, 'oid'), \
                               config.get(check, 'description'), \
                               config.get(check, 'system'))
