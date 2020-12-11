# -*- coding: utf-8 -*-

import json
from collections import OrderedDict

from six import string_types

from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('tool', 'templates'))


def space_str(layer):
    spaces = ""
    for i in range(0, layer):
        spaces += '\t'
    return spaces

def dic_to_lua_str(data, layer=0, field_meta={}):
    d_type = type(data)

    if isinstance(data, string_types):
        yield ("'" + data + "'")

    elif d_type is bool:
        if data:
            yield ('true')
        else:
            yield ('false')
    elif d_type is int or d_type is float:
        yield (str(data))
    elif d_type is list:
        yield ("{\n")
        yield (space_str(layer + 1))
        for i in range(0, len(data)):
            # index_str = '[' + str(i) + ']='
            # yield index_str
            for sub in dic_to_lua_str(data[i], layer + 1):
                yield sub
            if i < len(data) - 1:
                yield (',\n')
                yield (space_str(layer + 1))
        yield ('\n')
        yield (space_str(layer))
        yield ('}')
    elif d_type is dict:
        yield ("\n")
        yield (space_str(layer))
        yield ("{\n")
        data_len = len(data)
        data_count = 0
        for k, v in data.items():

            data_count += 1
            yield (space_str(layer + 1))
            if type(k) is int:
                yield ('[' + str(k) + ']')
            else:
                yield (k)
            yield (' = ')

            # lua type 特殊处理
            if field_meta and field_meta[k]['type'] == 'lua':
                yield v
                if data_count < data_len:
                    yield (',\n')
                continue

            try:
                for sub in dic_to_lua_str(v, layer + 1):
                    yield sub
                if data_count < data_len:
                    yield (',\n')

            except Exception as e:
                print('error in ', k, v)
                raise
        yield ('\n')
        yield (space_str(layer))
        yield ('}')
    else:
        # raise d_type, 'is error'
        # raise  Exception()
        print(d_type,'is error')


def render_py(jsonStr, fieldMetaStr="{}"):
    field_meta = json.loads(fieldMetaStr)

    return field_meta['sheet_name'] + "=" + jsonStr


def render_json(jsonStr, fieldMetaStr="{}"):
    field_meta = json.loads(fieldMetaStr)

    return field_meta['sheet_name'] + "=" + jsonStr


def render_lua(jsonStr, fieldMetaStr="{}"):
    field_meta = json.loads(fieldMetaStr).get('field_meta', {})

    data_dic = OrderedDict(json.loads(jsonStr))
    is_str = False
    for key in data_dic:
        try:
            int(key)
        except Exception as e:
            is_str = True

        bytes = ""

        for it in dic_to_lua_str(data_dic[key], 0, field_meta):
            bytes += it
        data_dic[key] = bytes
    tpl = env.get_template('lua_template.html')

    return tpl.render(data_dic=data_dic, is_str=is_str)


def render_manifest(jsonStr):
    tpl = env.get_template('manifest.html')
    return tpl.render(content=jsonStr)
