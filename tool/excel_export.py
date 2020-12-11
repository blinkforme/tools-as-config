# -*- coding: utf-8 -*-


import json
import os
import sys
import time
from collections import OrderedDict

import xlrd

reload(sys)
sys.setdefaultencoding('utf-8')
PROJECT_PATH = os.getcwd()
APPS_PATH = os.path.dirname(PROJECT_PATH)
sys.path.extend([PROJECT_PATH, APPS_PATH])

from assassin import write_file
from json_to_as3 import str_to_as3_class, str_to_as3_class_lang
from json_to_lua import render_lua, render_manifest, render_py

TARGET_PATHS = []
AS3_CLAZZ_TARGET_PATHS = []
SERVER_PATH = ''
PY_SERVER_PATH = ''
JSON_SERVER_PATH = ''

# manager路径
CONFIG_MANAGER_PATH = ""

EXCEL_PATH = ""
CACHE_JSON_PATH = ""

# 导出的config存一分在此文件夹，用于jenkins发布
PRODUCT_PATH = ""

EXPORT_TYPE = 0
HAVE_EXPORT_TYPE = False

# 是否是多语言版本
IS_LANG_TEMPLATE = False


def get_all_excels():
    walk_path = EXCEL_PATH
    paths = []
    for (dirpath, dirnames, filenames) in os.walk(walk_path):
        for f in filenames:
            if not f.startswith('~') and not f.startswith('.'):
                paths.append(os.path.join(walk_path, f))

    return paths


def process_float(value):
    if type(value) == float:
        if value == int(value):
            value = int(value)
            return value

    return value


def transform_type(field_type, value):
    if field_type == 'int':
        try:
            if value != "":
                value = int(value)
        except Exception as e:
            print('can not convert to int')
            raise e
    elif field_type in ['str', "string"]:
        value = unicode(value)

    elif field_type == "int_arr":
        value = str(process_float(value))
        if value:
            result = []
            for item in value.split(','):
                if item:
                    result.append(int(item))
            return result
        else:
            return []

    elif field_type == "float_arr":
        if value:
            value = str(value)
            value = [float(item) for item in value.split(',')]
        else:
            value = []

    elif field_type == "str_arr":
        if value:
            value = value.split(',')
        else:
            value = []

    elif field_type in ["float", "double"]:
        value = float(value)
    elif field_type == "json":
        value = json.loads(value)
    return value


def column_string(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string


def process_sheet(sh):
    client_dic = OrderedDict()
    server_dic = OrderedDict()

    # 兼容新老表格格式
    start_row = 4
    if HAVE_EXPORT_TYPE:
        start_row = 5

    desc_rows = sh.row_values(0)
    id_rows = sh.row_values(1)
    target_rows = sh.row_values(2)
    type_rows = sh.row_values(3)
    for rownum in range(start_row, sh.nrows):
        row_values = sh.row_values(rownum)

        if row_values[0] == "" or row_values[0] == None:
            continue
        server_obj = {}
        client_obj = {}

        for i, element in enumerate(row_values):

            target = target_rows[i]
            field_name = id_rows[i]
            field_type = type_rows[i]

            try:
                value = transform_type(format_type(field_type), element)
            except Exception as e:
                print (("convert type error, table name：{sheet_name} , {rownum} row {column} column ({desc})"
                        .format(sheet_name=sh.name, rownum=rownum + 1, column=column_string(i + 1),
                                desc=desc_rows[i])))

                print (("type：" + type_rows[i]))
                print (("your value：" + element))
                print("wtf？")
                raise e

            if 's' in target:
                server_obj[field_name] = value
            if 'c' in target and field_type not in ["lua"]:
                client_obj[field_name] = value

        client_dic[client_obj["id"]] = client_obj
        server_dic[server_obj["id"]] = server_obj

    client_content = json.dumps(client_dic, indent=4)
    server_content = json.dumps(server_dic, indent=4)
    return client_content, server_content


# 规整类型
def format_type(type):
    type = type.strip().upper()
    if type in ['INT', 'INTEGER']:
        return 'int'
    if type in ['STR', 'STRING']:
        return 'string'
    if type in ['FLOAT', 'DOUBLE']:
        return 'double'
    if type in ['JSON']:
        return 'json'
    if type in ['STRING_ARR', 'STR_ARR']:
        return 'str_arr'
    if type in ['INT_ARR', 'INTEGER_ARR']:
        return 'int_arr'
    if type in ['FLOAT_ARR', 'FLOAT_ARRAY']:
        return 'float_arr'
    if type in ["LUA"]:
        return 'lua'
    return type.strip()


def type_to_as3_type(type):
    type = format_type(type.strip())
    dic = {
        'int': 'int',
        'string': 'String',
        'float': "Number",
        'double': 'Number',
        'str_arr': 'Array',
        'int_arr': 'Array',
        "float_arr": "Array"
    }
    return dic.get(type, 'Object')


# 导出表格元数据
def process_sheet_metadata(sh):
    sheet_mate = {}
    field_meta = {}

    pk_name = sh.col_values(0)[1]
    field_type = sh.col_values(0)[3]
    field_meta[pk_name] = {
        'target': "sc",
        'type': format_type(field_type),
        'as3_type': type_to_as3_type(field_type)
    }

    for column in range(1, sh.ncols):
        col_values = sh.col_values(column)
        field_name = col_values[1]
        field_target = col_values[2]
        field_type = col_values[3]

        field_meta[field_name] = {
            'target': field_target,
            'type': format_type(field_type),
            'as3_type': type_to_as3_type(field_type)
        }

    sheet_mate['field_meta'] = field_meta
    sheet_mate['sheet_name'] = sh.name
    return json.dumps(sheet_mate, indent=4)


def create_folder():
    """
    创建路径
    :return:
    """
    if TARGET_PATHS:
        for path in TARGET_PATHS:
            if not os.path.exists(path):
                os.makedirs(path)
    if AS3_CLAZZ_TARGET_PATHS:
        for path in AS3_CLAZZ_TARGET_PATHS:
            if not os.path.exists(path):
                os.makedirs(path)

    if SERVER_PATH and not os.path.exists(SERVER_PATH):
        os.makedirs(SERVER_PATH)

    if PY_SERVER_PATH and not os.path.exists(PY_SERVER_PATH):
        os.makedirs(PY_SERVER_PATH)

    if JSON_SERVER_PATH and not os.path.exists(JSON_SERVER_PATH):
        os.makedirs(JSON_SERVER_PATH)

    # if CACHE_JSON_PATH and not os.path.exists(CACHE_JSON_PATH):
    #     os.makedirs(CACHE_JSON_PATH)

    if PRODUCT_PATH and not os.path.exists(PRODUCT_PATH):
        os.makedirs(PRODUCT_PATH)


# 客户端内容
all_json_content = {}


def confusion_json(js_content, field_mate):
    """
    去掉配表的KEY，做一定的混淆
    :param js_content:
    :param field_mate:
    :return:
    """

    meta = json.loads(field_mate)
    meta_data = meta["field_meta"]
    meta2 = {"field_meta": {}, "sheet_name": meta["sheet_name"]}
    meta_data2 = meta2["field_meta"]

    dic = json.loads(js_content)
    index = 0

    for k, obj in dic.iteritems():
        for key in obj.keys():
            d = meta_data[key].copy()
            if "c" in d["target"]:
                meta_data2[key] = meta_data[key].copy()
                meta_data2[key]["confusion_index"] = index

                index = index + 1
        break

    dic_temp = {}
    for k, obj in dic.iteritems():
        obj2 = [None] * len(obj.keys())
        for key in obj.keys():
            confusion_index = meta_data2[key]["confusion_index"]

            obj2[confusion_index] = obj[key]
        dic_temp[k] = obj2

    return dic_temp, meta2


def process_xlsx(file_path):
    # begin = getCurMillSecond()

    wb = xlrd.open_workbook(file_path)

    # end = getCurMillSecond()
    # print("cost confusion_json:" + str(end - begin))

    sheets = []

    for s in wb.sheets():
        sheet_name = s.name
        # 跳过测试页面
        if not sheet_name.startswith("cfg") and not sheet_name.startswith("s_cfg"):
            continue

        is_server_only = False
        if sheet_name.startswith("s_cfg"):
            is_server_only = True
            sheet_name = sheet_name[2:]

        sheets.append(sheet_name)

        # 处理表格

        client_content, server_content = process_sheet(s)

        field_mate = process_sheet_metadata(s)

        # 混淆代码
        confusion_data, confusion_meta = confusion_json(client_content, field_mate)

        if not is_server_only:
            all_json_content[sheet_name] = confusion_data

        # 导出服务端lua数据
        if SERVER_PATH:
            lua_file_name = os.path.join(SERVER_PATH, '{file_name}.lua'.format(file_name=sheet_name))
            write_file(render_lua(server_content, field_mate), lua_file_name)

        # 导出服务端PY数据
        if PY_SERVER_PATH:
            py_file_name = os.path.join(PY_SERVER_PATH, '{file_name}.py'.format(file_name=sheet_name))
            write_file(render_py(server_content, field_mate), py_file_name)

        # 导出服务端JSON数据
        if JSON_SERVER_PATH:
            json_file_name = os.path.join(JSON_SERVER_PATH, '{file_name}.json'.format(file_name=sheet_name))
            write_file(server_content, json_file_name)

        # 导出JSON数据，用于检查表冲突
        # json_file_name2 = os.path.join(CACHE_JSON_PATH, '{file_name}.json'.format(file_name=sheet_name))
        # write_file(server_content, json_file_name2)

        if not is_server_only:
            # 导出AS3配表对象
            for path in AS3_CLAZZ_TARGET_PATHS:
                as3_file_path = os.path.join(path, "{file_name}.as".format(file_name=sheet_name))
                if IS_LANG_TEMPLATE:
                    write_file(str_to_as3_class_lang(confusion_meta,CONFIG_MANAGER_PATH), as3_file_path)
                else:
                    write_file(str_to_as3_class(confusion_meta,CONFIG_MANAGER_PATH), as3_file_path)

    wb.release_resources()
    return sheets


def getCurMillSecond():
    return int(time.time() * 1000)


def entry():
    manifest = []

    # 处理EXCEl

    begin = getCurMillSecond()
    # 处理EXCEl
    for file_path in EXCEL_FILE_NAMES:
        try:
            sheets = process_xlsx(file_path=file_path)
        except Exception as e:
            raise e
            print("process error:" + file_path)

        manifest.extend(sheets)
        print "process success:" + file_path

    end = getCurMillSecond()
    print("cost:" + str(end - begin))

    print ("------------------------>end")

    all_json_content["cfg_robotname"] = ""
    all_json_content["cfg_robot"] = ""

    if TARGET_PATHS:
        for path in TARGET_PATHS:
            write_file(json.dumps(all_json_content, separators=(',', ':')), os.path.join(path, "config.json"))

    # 导出配表到product文件夹，用于jenkins发布
    write_file(json.dumps(all_json_content, separators=(',', ':')), os.path.join(PRODUCT_PATH, "config.json"))

    if AS3_CLAZZ_TARGET_PATHS:
        for path in AS3_CLAZZ_TARGET_PATHS:
            write_file(render_manifest(manifest), os.path.join(path, 'manifest.as'))
    print '\n--------------------------------------------------------------------'
    print "{len} documents were processed this time".format(len=len(manifest))


if __name__ == '__main__':
    project_name = ""
    # global EXPORT_TYPE
    # global HAVE_EXPORT_TYPE

    if len(sys.argv) > 1:
        project_name = sys.argv[1]

    if len(sys.argv) > 2:
        HAVE_EXPORT_TYPE = True
        EXPORT_TYPE = int(sys.argv[2])

    names = ["trials", "trials-weibo",  'test', 'abomination', "deathknight","sylvanas", "thief", "lich", "warden",'weapon_card', 'archer','answer','box-game']
    if project_name not in names:
        raise Exception("parameter error ，should be in " + '|'.join(names))

    import importlib

    config = importlib.import_module('resource.' + project_name + '.config')

    TARGET_PATHS = getattr(config, "TARGET_PATHS", [])

    AS3_CLAZZ_TARGET_PATHS = getattr(config, "AS3_CLAZZ_TARGET_PATHS", [])

    SERVER_PATH = getattr(config, "SERVER_PATH", None)
    PY_SERVER_PATH = getattr(config, "PY_SERVER_PATH", None)
    JSON_SERVER_PATH = getattr(config, "JSON_SERVER_PATH", None)

    CONFIG_MANAGER_PATH = getattr(config, "CONFIG_MANAGER_PATH", "manager")

    timestamp_names = ["trials-weibo", 'abbey_os']
    # if project_name in timestamp_names:
    #     JSON_SERVER_PATH += str(int(time.time()))
    #     print '按照时间戳归档 ' + JSON_SERVER_PATH

    EXCEL_PATH = 'resource/' + project_name + '/excels/'
    CACHE_JSON_PATH = os.path.join(os.path.abspath(os.curdir), 'resource', project_name, 'jsons')

    PRODUCT_PATH = os.path.join(os.path.abspath(os.curdir), 'product', project_name)

    print "CACHE_JSON_PATH", CACHE_JSON_PATH
    EXCEL_FILE_NAMES = get_all_excels()

    if project_name in ["abbey_os", "client_happy"]:
        IS_LANG_TEMPLATE = True

    create_folder()
    entry()
