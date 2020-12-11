# -*- coding: utf-8 -*-



class MemberDescriptor():

    PROTOBUF_TYPES = ["sint32", "sint64", "float", "int32", "int64", "uint32", "uint64", "string","bool"]

    NUMBER_TYPES = ["sint32", "sint64", "float", "int32", "int64", "uint32", "uint64"]
    def __init__(self, index, qualifier, name, type, mapArgs):
        self.index = index
        self.name = name
        self.type = type
        self.qualifier = qualifier
        self.mapArgs = mapArgs

    def to_as3_type(self):
        if self.type.lower() in self.NUMBER_TYPES:
            return "Number"
        if self.type.lower() in ["string"]:
            return "String"
        if self.type.lower() in ["map"]:
            return "Object"
        if self.type.lower() == "bool":
            return "Boolean"
        else:
            return self.type

    def is_repeated(self):
        return self.qualifier == "repeated"

    def is_map(self):
        return self.type == "map"

    def is_single_type(self):
        """
        是否是protobuf内置的类型
        :return:
        """
        return self.type.lower() in self.PROTOBUF_TYPES

    def _to_as3_writer_func_by_type(self,type):
        if type.lower() in ["sint32", "sint64"]:
            if self.is_repeated():
                return "writeRepeatedSint32"
            else:
                return "writeSint32"
        if type.lower() in ["string"]:
            if self.is_repeated():
                return "writeRepeatedString"
            else:
                return "writeString"
        if type.lower() in ["float"]:
            if self.is_repeated():
                return "writeRepeatedFloat"
            else:
                return "writeFloat"
        if type.lower() in ["bool"]:
            if self.is_repeated():
                return "writeRepeatedBool"
            else:
                return "writeBool"
        else:
            if self.is_map():
                return "writeBinary"
            else:
                if self.is_repeated():
                    return "writeRepeatedMessage"
                else:
                    return "writeMessage"

    def _to_as3_reader_func_by_type(self, type):
        if type.lower() in ["sint32", "sint64"]:
            return "readSint32"
        if type.lower() in ["string"]:
            return "readString"
        if type.lower() in ["float"]:
            return "readFloat"
        if type.lower() in ["bool"]:
            return "readBool"
        else:
            return "readMessage"

    def to_as3_writer_func(self):
        """
        获取as3写入函数
        :return:
        """
        return self._to_as3_writer_func_by_type(self.type)

    def to_as3_reader_func(self):
        """
        获取as3读取函数
        :return:
        """
        return self._to_as3_reader_func_by_type(self.type)

    def to_as3_map_key_reader_func(self):
        """
        获取map的key读取函数
        :return:
        """
        if len(self.mapArgs) == 2:
            return self._to_as3_reader_func_by_type(self.mapArgs[0])

        raise Exception("to_as3_map_key_reader_func")

    def to_as3_map_value_reader_func(self):
        """
       获取map的value读取函数
       :return:
       """
        if len(self.mapArgs) == 2:
            return self._to_as3_reader_func_by_type(self.mapArgs[1])

        raise Exception("to_as3_map_value_reader_func")

    def to_as3_map_constructor_func(self):
        """

        :return:
        """
        if len(self.mapArgs) == 2:
            type = self.mapArgs[1]
            if type in self.PROTOBUF_TYPES:
                return  "null"
            else:
                return  type
        raise Exception("to_as3_map_constructor_func")

class MessageDescriptor():
    def __init__(self, name):
        self.members = []
        self.name = name

    def addMember(self, varOrder, varQualifier, varName, varType, mapArgs=[]):
        member = MemberDescriptor(varOrder, varQualifier, varName, varType, mapArgs)
        self.members.append(member)


class PbAst():
    def __init__(self):
        self.messages = {}

    def addMessage(self, md):
        """

        :param md: MemberDescriptor
        :return:
        """
        self.messages[md.name] = md

    def isMessageExist(self, name):
        if self.messages.get(name, None):
            return True
        else:
            return False
