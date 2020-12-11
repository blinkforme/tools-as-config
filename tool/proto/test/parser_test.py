# -*- coding: utf-8 -*-

from tool.proto.PbLexer import PbLexer
from tool.proto.PbParser import PbParser

content = """

message ItemData {
    required sint32 good_id = 1;
    required sint32 good_num = 2;
    required ItemData data = 3;

}
//红点协议
message s2c_19006 {
    optional sint32 red_points = 1;
    optional string xxx = 2;
    repeated ItemData items = 3;
    optional float num = 4;
}

message s2c_19007 {
    optional sint32 fuck = 1;

}


"""

content2 = """

message ItemDataF {
    required sint32 good_id = 1;

}



"""

lexer = PbLexer(content=content, fileName="test.proto")

parser = PbParser()
parser.parse(content=content, fileName="test.proto")
parser.parse(content=content2, fileName="test.proto")

ast = parser.ast

for index, key in enumerate(ast.messages):
    message = ast.messages[key]
    print key
    for index, member in enumerate(message.members):
        print member.qualifier, member.type, member.name, member.index
    print "-" * 20