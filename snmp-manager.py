#!/usr/bin/env python2
# -*- encoding: utf8 -*-

import sys, os.path, time
import rrdtool
from ConfigParser import SafeConfigParser
from pysnmp.entity.rfc3413.oneliner import cmdgen

class SnmpManager:
    def __init__(self):
        self.systems = {}
        self.databases_initialized = False

    def add_system(self, id_, desc, addr, port, comm_ro):
        self.systems[id_] = {\
            'description': desc,\
            'address': addr,\
            'port': int(port),\
            'communityro': comm_ro,\
            'checks': {},\
        }

    def add_check(self, id_, oid, desc, system, sampling_rate):
        oid_tuple = tuple([int(i) for i in oid.split('.')])
        self.systems[system]['checks'][id_] = {\
            'description': desc,\
            'oid': oid_tuple,\
            'sampling_rate': sampling_rate,\
        }

    def query_all_systems(self):
        if not self.databases_initialized:
            self.initialize_databases()
            self.databases_initialized = True
        cg = cmdgen.CommandGenerator()
        for system in self.systems.values():
            comm_data = cmdgen.CommunityData('my-manager', system['communityro'])
            transport = cmdgen.UdpTransportTarget((system['address'], system['port']))
            for key, check in system['checks'].iteritems():
                oid = check['oid']
                errInd, errStatus, errIdx, result = cg.getCmd(comm_data, transport, oid)
                if not errInd and not errStatus:
                    file_name = 'rrdtool/{key}.rrd'.format(key=key)
                    rrdtool.update(file_name, '{time}:{value}'.format(time=int(time.time()),\
                                                                      value=int(result[0][1]))\
                                                                      )
    def initialize_databases(self):
        for system in self.systems.values():
            for check in system['checks']:
                data_file = 'rrdtool/{check}.rrd'.format(check=check)
                if not os.path.isfile(data_file):
                    print data_file, 'does not exist'
                    rrdtool.create(data_file,\
                                   'DS:{check}:COUNTER:{step}:U:U'.format(\
                                            check=check,\
                                            step=system['checks'][check]['sampling_rate']),
                                    'RRA:AVERAGE:0.5:1:288')

def main(conf_file=""):
    if not conf_file:
        sys.exit(-1)
    config = SafeConfigParser()
    config.read(conf_file)
    snmp_manager = SnmpManager()
    for system in (s for s in config.sections() if s.startswith('system')):
        snmp_manager.add_system(system,\
                                config.get(system, 'description'),\
                                config.get(system, 'address'),\
                                config.get(system, 'port'),\
                                config.get(system, 'communityro'))
    for check in (c for c in config.sections() if c.startswith('check')):
        snmp_manager.add_check(check,\
                               config.get(check, 'oid'),\
                               config.get(check, 'description'),\
                               config.get(check, 'system'),\
                               config.get(check, 'sampling_rate'))
    snmp_manager.query_all_systems()

if __name__ == '__main__':
    main(conf_file='snmp-manager.cfg')
