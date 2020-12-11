# -*- coding: utf-8 -*-
import json
from collections import OrderedDict


class DataSet:
    as3TypeMap = {
        'int': 'int',
        'string': 'String',
        'float': "Number",
        'double': 'Number',
        'str_arr': 'Array',
        'int_arr': 'Array',
        "float_arr": "Array"
    }

    def __init__(self, table_name, note_line, field_line, target_line, type_line, data_lines):
        """
        :param table_name:表名
        :param note_line:注释行
        :param field_line:字段行
        :param target_line:导出目标行
        :param type_line:类型行
        :param data_lines:数据行
        """

        self.origin_table_name = table_name
        self.table_name = table_name
        self.note_line = note_line
        self.field_line = field_line
        self.target_line = target_line
        self.type_line = type_line
        self.data_lines = data_lines

        if self.is_server_only():
            self.table_name = self.origin_table_name[2:]
        else:
            self.table_name = self.origin_table_name

        # 特殊处理主键、LUA字段
        for i in range(len(self.type_line)):
            if i == 0:
                self.target_line[i] = "sc"
            if self.type_line[i] == "lua":
                self.target_line[i] = "s"

    def is_server_only(self):
        if self.origin_table_name.startswith("s_cfg"):
            return True
        else:
            return False

    def type_to_as3_type(self, type):
        return self.as3TypeMap.get(self.format_type(type), 'Object')

    def field_meta(self, target):
        """
        获取表的元数据
        :return:
        """
        sheet_mate = OrderedDict()
        field_meta = OrderedDict()

        index = 0
        for i, field in enumerate(self.field_line):
            field_type = self.type_line[i]
            field_target = self.target_line[i]

            if target == "sc":
                field_meta[field] = {
                    'target': field_target,
                    'type': self.format_type(field_type),
                    'as3_type': self.type_to_as3_type(field_type),
                    "confusion_index": index
                }
                index = index + 1
            else:
                if target in field_target:
                    field_meta[field] = {
                        'target': field_target,
                        'type': self.format_type(field_type),
                        'as3_type': self.type_to_as3_type(field_type),
                        "confusion_index": index
                    }
                    index = index + 1

        sheet_mate['field_meta'] = field_meta
        sheet_mate['sheet_name'] = self.table_name

        return sheet_mate

    def to_all_json(self):
        dic = OrderedDict()

        for data_line in self.data_lines:
            id = self.transform_type(self.format_type(self.type_line[0]), data_line[0])
            data = OrderedDict()

            for i, item in enumerate(data_line):
                key = self.field_line[i]
                type = self.type_line[i]
                field_target = self.target_line[i]
                data[key] = self.transform_type(type, item)

            dic[id] = data

        return dic

    def to_json(self, target):
        dic = OrderedDict()

        for data_line in self.data_lines:
            id = self.transform_type(self.format_type(self.type_line[0]), data_line[0])
            data = OrderedDict()

            for i, item in enumerate(data_line):
                key = self.field_line[i]
                type = self.type_line[i]
                field_target = self.target_line[i]
                if target in field_target:
                    data[key] = self.transform_type(type, item)
                else:
                    continue
            dic[id] = data

        return dic

    def format_type(self, type):
        type = type.strip().upper()
        if type in ['INT', 'INTEGER']:
            return 'int'
        elif type in ['STR', 'STRING']:
            return 'string'
        elif type in ['FLOAT', 'DOUBLE']:
            return 'double'
        elif type in ['JSON']:
            return 'json'
        elif type in ['STRING_ARR', 'STR_ARR']:
            return 'str_arr'
        elif type in ['INT_ARR', 'INTEGER_ARR']:
            return 'int_arr'
        elif type in ['FLOAT_ARR', 'FLOAT_ARRAY']:
            return 'float_arr'
        elif type in ["LUA"]:
            return 'lua'
        else:
            return type.strip()

    def process_float(self, value):
        if type(value) == float:
            if value == int(value):
                value = int(value)
                return value

        return value

    def transform_type(self, field_type, value):
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

            value = str(self.process_float(value))

            if value:
                if value[0] == "{" and value[-1] == "}":
                    value = value[1:-1]

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
                if value[0] == "{" and value[-1] == "}":
                    value = value[1:-1]

                value = [float(item) for item in value.split(',')]
            else:
                value = []

        elif field_type == "str_arr":
            if value:
                if value[0] == "{" and value[-1] == "}":
                    value = value[1:-1]

                value = value.split(',')
            else:
                value = []

        elif field_type in ["float", "double"]:
            value = float(value)
        elif field_type == "json":
            value = json.loads(value)
        return value
