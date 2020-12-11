# -*- coding: utf-8 -*-

import os
import sys

from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('tool', 'templates'))

PROJECT_PATH = os.getcwd()
APPS_PATH = os.path.dirname(PROJECT_PATH)
sys.path.extend([PROJECT_PATH, APPS_PATH])


def str_to_as3_class(sheet_meta,CONFIG_MANAGER_PATH):
    tpl = env.get_template('class_ts.html')
    return tpl.render(sheet_meta=sheet_meta,CONFIG_MANAGER_PATH=CONFIG_MANAGER_PATH)


def render_manifest_ts(jsonStr):
    tpl = env.get_template('manifest_ts.html')
    return tpl.render(content=jsonStr)

def str_to_ts_class_lang(sheet_meta,CONFIG_MANAGER_PATH):
    tpl = env.get_template('class_lang.html')
    return tpl.render(sheet_meta=sheet_meta,CONFIG_MANAGER_PATH=CONFIG_MANAGER_PATH)