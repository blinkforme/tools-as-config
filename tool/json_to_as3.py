# -*- coding: utf-8 -*-

import os
import sys

from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('tool', 'templates'))

PROJECT_PATH = os.getcwd()
APPS_PATH = os.path.dirname(PROJECT_PATH)
sys.path.extend([PROJECT_PATH, APPS_PATH])


def str_to_as3_class_funk_lang(sheet_meta,CONFIG_MANAGER_PATH):
    tpl = env.get_template('class2_lang.html')
    return tpl.render(sheet_meta=sheet_meta,CONFIG_MANAGER_PATH=CONFIG_MANAGER_PATH)


def str_to_as3_class_funk(sheet_meta,CONFIG_MANAGER_PATH):
    tpl = env.get_template('class2.html')
    return tpl.render(sheet_meta=sheet_meta,CONFIG_MANAGER_PATH=CONFIG_MANAGER_PATH)


def str_to_as3_class(sheet_meta,CONFIG_MANAGER_PATH):
    tpl = env.get_template('class.html')
    return tpl.render(sheet_meta=sheet_meta,CONFIG_MANAGER_PATH=CONFIG_MANAGER_PATH)


def str_to_as3_class_lang(sheet_meta,CONFIG_MANAGER_PATH):
    tpl = env.get_template('class_lang.html')
    return tpl.render(sheet_meta=sheet_meta,CONFIG_MANAGER_PATH=CONFIG_MANAGER_PATH)