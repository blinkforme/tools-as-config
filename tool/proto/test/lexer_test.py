# -*- coding: utf-8 -*-

from tool.proto.PbLexer import PbLexer

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

lexer = PbLexer(content=content, fileName="test.proto")
while True:
    token = lexer.parseToken()
    if token:
        print lexer.value
        print token
        print "--------------"
    else:
        break