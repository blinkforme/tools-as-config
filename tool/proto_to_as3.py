# -*- coding: utf-8 -*-

import os
import sys

from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('tool', 'templates'))

PROJECT_PATH = os.getcwd()
APPS_PATH = os.path.dirname(PROJECT_PATH)
sys.path.extend([PROJECT_PATH, APPS_PATH])


def str_to_as3_proto_s2c_class(message):
    tpl = env.get_template('proto_s2c.html')
    return tpl.render(message=message)


def str_to_as3_proto_c2s_class(message):
    tpl = env.get_template('proto_c2s.html')
    return tpl.render(message=message)


def render_register(messages):
    tpl = env.get_template('proto_register.html')
    return tpl.render(messages=messages)