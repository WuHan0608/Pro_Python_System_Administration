#!/usr/bin/env python2
# -*- encoding: utf8 -*-

from jinja2 import Environment, FileSystemLoader
from ConfigParser import SafeConfigParser
import rrdtool
import sys, os.path

WEBSITE_ROOT = os.path.join(os.path.expanduser('~'), 'public_html', 'snmp-monitor')

def generate_index(systems, env, website_root):
    template = env.get_template('templates/index.tpl')
    with open(os.path.join(website_root, 'index.html'), 'w') as fp:
        fp.write(template.render({'systems': systems}))

def generate_details(system, env, website_root):
    template = env.get_template('templates/details.tpl')
    for check_name, check_obj in system['checks'].iteritems():
        rrdtool.graph('{website}/{name}.png'.format(\
                                website=website_root,\
                                name=check_name),\
                      '--title', check_obj['description'],\
                      'DEF:data={path}.rrd:{name}:AVERAGE'.format(\
                                path=os.path.join('rrdtool', check_name),\
                                name=check_name),\
                      'AREA:data#0c0c0c')
        with open(os.path.join(website_root, '{name}.html'.format(name=check_name)), 'w') as fp:
            fp.write(template.render({'check': check_obj, 'name': check_name}))

def generate_website(conf_file='', website_root=WEBSITE_ROOT):
    if not conf_file:
        sys.exit(-1)
    config = SafeConfigParser()
    config.read(conf_file)
    loader = FileSystemLoader('.')
    env = Environment(loader=loader)
    systems = {}
    for system in (s for s in config.sections() if s.startswith('system')):
        systems[system] = {\
            'description': config.get(system, 'description'),\
            'address': config.get(system, 'address'),\
            'port': config.get(system, 'port'),\
            'checks': {},\
        }
    for check in (c for c in config.sections() if c.startswith('check')):
        systems[config.get(check, 'system')]['checks'][check] = {\
           'oid': config.get(check, 'oid'),\
           'description': config.get(check, 'description'),\
        }
    generate_index(systems, env, website_root)
    for system in systems.values():
        generate_details(system, env, website_root)

if __name__ == '__main__':
    generate_website(conf_file='snmp-manager.cfg')
