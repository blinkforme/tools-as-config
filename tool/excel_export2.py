# -*- coding: utf-8 -*-
import json
import os
import sys
import time
import xlrd

import csv

import sys

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

PROJECT_PATH = os.getcwd()
APPS_PATH = os.path.dirname(PROJECT_PATH)
sys.path.extend([PROJECT_PATH, APPS_PATH])

from DataSet import DataSet
from ResConfig import ResConfig

from assassin import write_file
from json_to_as3 import str_to_as3_class, str_to_as3_class_lang, str_to_as3_class_funk, str_to_as3_class_funk_lang
from json_to_lua2 import render_lua, render_manifest, render_lua_unity, render_unity_manifest
import excel_export2_config  as config_map

config = None

# 客户端内容
all_json_content = {}


def confusion_json(js_dic, sheet_meta):
    """
    去掉配表的KEY，做一定的混淆
    :param js_content:
    :param field_mate:
    :return:
    """

    meta_data = sheet_meta["field_meta"]

    dic_temp = {}
    for k, obj in js_dic.iteritems():
        obj2 = []
        for field in obj.keys():
            if "c" in meta_data[field]["target"]:
                obj2.append(obj[field])
        dic_temp[k] = obj2

    return dic_temp, sheet_meta


def getCurMillSecond():
    return int(time.time() * 1000)


def get_file_type(file_path):
    suffix = os.path.splitext(file_path)[-1]
    if "xlsx" in suffix:
        return "xlsx"
    elif "csv" in suffix:
        return "csv"
    else:
        return None


def get_ds_from_csv(file_path):
    with open(file_path, 'rU') as myFile:
        reader = csv.reader(myFile)

        result = []
        data_arr = []

        for i, line in enumerate(reader):

            if i < 4:
                result.append(line)
            else:
                if line[0] == "" or line[0] is None:
                    continue
                data_arr.append(line)

        table_name = os.path.splitext(os.path.split(file_path)[1])[0]
        t = DataSet(table_name, result[0], result[1], result[2], result[3], data_arr)

        return t


def get_ds_from_excel(file_path):
    wb = xlrd.open_workbook(file_path)

    s = wb.sheets()[0]

    result = []
    data_arr = []
    for num in range(0, s.nrows):
        if num < 4:
            result.append(s.row_values(num))
        else:
            if s.row_values(num)[0] == "" or s.row_values(num)[0] is None:
                continue
            data_arr.append(s.row_values(num))

    t = DataSet(s.name, result[0], result[1], result[2], result[3], data_arr)

    return t


def process_dt(t):
    client_obj = t.to_json("c")
    server_obj = t.to_json("s")
    all_obj = t.to_all_json()


    server_field_mate = t.field_meta("s")
    client_field_mate = t.field_meta("c")
    all_field_meta = t.field_meta("sc")
    # 混淆代码
    confusion_data, confusion_meta = confusion_json(client_obj, client_field_mate)

    if not t.is_server_only():
        all_json_content[t.table_name] = confusion_data

    # 导出服务端lua数据 会改变server_obj,这里需要copy一个来导出
    if config.JSON_SERVER_PATH:
        json_file_name = os.path.join(config.JSON_SERVER_PATH, '{file_name}.json'.format(file_name=t.table_name))
        write_file(json.dumps(all_obj), json_file_name)

    # 导出服务端lua数据
    # 2020-1-9导出服务端lua数据 会改变server_obj,这里需要copy一个来导出

    if config.SERVER_PATH:
        lua_file_name = os.path.join(config.SERVER_PATH, '{file_name}.lua'.format(file_name=t.table_name))
        write_file(render_lua(server_obj.copy(), server_field_mate), lua_file_name)

    if config.UNITY_PATH:
        for path in config.UNITY_PATH:
            lua_file_name = os.path.join(path, '{file_name}.lua'.format(file_name=t.table_name))
            write_file(render_lua_unity(client_obj.copy(), all_field_meta), lua_file_name)


    if not t.is_server_only():
        # 导出AS3配表对象
        for path in config.AS3_CLAZZ_TARGET_PATHS:
            as3_file_path = os.path.join(path, "{file_name}.as".format(file_name=t.table_name))

            if config.IS_FUNK_TEMPLATE:
                if config.IS_LANG_TEMPLATE:
                    write_file(str_to_as3_class_funk_lang(confusion_meta, config.CONFIG_MANAGER_PATH), as3_file_path)
                else:
                    write_file(str_to_as3_class_funk(confusion_meta, config.CONFIG_MANAGER_PATH), as3_file_path)


            else:
                if config.IS_LANG_TEMPLATE:
                    write_file(str_to_as3_class_lang(confusion_meta, config.CONFIG_MANAGER_PATH), as3_file_path)
                else:
                    write_file(str_to_as3_class(confusion_meta, config.CONFIG_MANAGER_PATH), as3_file_path)


def entry():
    manifest = []

    # 处理EXCEl
    begin = getCurMillSecond()

    for file_path in config.EXCEL_FILE_NAMES:
        print("start process:" + file_path)

        file_type = get_file_type(file_path)
        if file_type == "xlsx":
            t = get_ds_from_excel(file_path=file_path)
        elif file_type == "csv":
            t = get_ds_from_csv(file_path=file_path)

        if t is None:
            continue

        process_dt(t)
        manifest.append(t.table_name)

        print "process success:" + file_path

    end = getCurMillSecond()
    print("cost:" + str(end - begin))

    print("------------------------>end")

    all_json_content["cfg_robotname"] = ""
    all_json_content["cfg_robot"] = ""

    if config.TARGET_PATHS:
        if config.FIRST_CONFIG:
            child_first_leaf = {}
            child_second_leaf = {}
            first_config = {}
            for name in config.FIRST_CONFIG:
                first_config[name] = ""
            for path in config.TARGET_PATHS:
                for cfgName in all_json_content:
                    if first_config.has_key(cfgName):
                        print("first json file contents: ", cfgName)
                        child_first_leaf[cfgName] = all_json_content[cfgName]
                    else:
                        child_second_leaf[cfgName] = all_json_content[cfgName]

            write_file(json.dumps(child_first_leaf, separators=(',', ':')), os.path.join(path, "first_config.json"))
            write_file(json.dumps(child_second_leaf, separators=(',', ':')), os.path.join(path, "second_config.json"))

        # 无论是否分表都导出单表
        for path in config.TARGET_PATHS:
            write_file(json.dumps(all_json_content, separators=(',', ':')), os.path.join(path, "config.json"))

    if config.AS3_CLAZZ_TARGET_PATHS:
        for path in config.AS3_CLAZZ_TARGET_PATHS:
            write_file(render_manifest(manifest), os.path.join(path, 'manifest.as'))

    if config.UNITY_PATH:
        for path in config.UNITY_PATH:
            write_file(render_unity_manifest(manifest), os.path.join(path, 'init_table.lua'))

    print "{len} documents were processed this time".format(len=len(manifest))


if __name__ == '__main__':
    project_name = ""

    if len(sys.argv) > 1:
        project_name = sys.argv[1]

    resource_path = getattr(config_map, project_name)
    if not resource_path:
        raise Exception("no config for " + project_name)
    print("resource_path", resource_path)

    config = ResConfig(res_path=resource_path)
    config.create_folder()

    entry()
