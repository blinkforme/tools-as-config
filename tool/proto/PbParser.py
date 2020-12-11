# -*- coding: utf-8 -*-

from PbLexer import *
from tool.proto.PbAst import MessageDescriptor, PbAst

VALID_VALUE_TOKENS = (
    T_IDENTITY,
    T_STRING,
    T_NUMBER,
    T_BOOLEAN
)

VALID_QUALIFIER_TOKENS = (
    T_REQUIRED,
    T_OPTIONAL,
    T_REPEATED
)


def is_expected_token(given, expected):
    if isinstance(expected, int) or isinstance(expected, str):
        return given == expected

    return given in expected


def is_identity_token(token):
    return token == T_IDENTITY or is_keyword_token(token)


class TokenInfo:
    def __init__(self, lexer):
        self.line = lexer.line
        self.column = lexer.column
        self.token = lexer.token
        self.value = lexer.value


class PbParser(object):
    def __init__(self):
        super(PbParser, self).__init__()

        self.lexer = None

        self.tokenInfo = None
        self.aheadTokenInfo = None

        self.ast = PbAst()

    def parse(self, content, fileName):
        self.content = content
        self.fileName = fileName


        self.lexer = PbLexer(self.content, self.fileName)

        tokenHandler = {
            ';': self.parseEmpty,
        }

        token = self.nextToken()
        while token is not None:

            handler = None

            if is_keyword_token(token):
                funName = "parse_" + token2str(token)
                handler = getattr(self, funName, None)

            if handler is None:
                handler = tokenHandler.get(token)

            if handler is None:
                self.error("Parser", "invalid token '%s'" % token2str(token))

            handler()
            token = self.nextToken()

        self.lexer = None

    def nextToken(self):
        if self.aheadTokenInfo:
            self.tokenInfo = self.aheadTokenInfo
            self.aheadTokenInfo = None
        else:
            self.lexer.next()
            self.tokenInfo = TokenInfo(self.lexer)
        return self.tokenInfo.token

    def lookAhead(self):
        if not self.aheadTokenInfo:
            self.lexer.next()
            self.aheadTokenInfo = TokenInfo(self.lexer)
        return self.aheadTokenInfo.token

    def matchNext(self, token, desc):
        self.matchToken(self.nextToken(), token, desc)

    def matchToken(self, given, expected, desc):
        ok = is_expected_token(given, expected)

        if ok: return

        if isinstance(expected, int):
            tokeName = token2str(expected)
        else:
            names = [token2str(tk) for tk in expected]
            tokeName = "|".join(names)
        self.error(desc, "token '%s' expected, but '%s' was given." % (tokeName, token2str(given)))
        return

    def parseEmpty(self, parent=None):
        pass

    def parse_message(self):
        desc = "message"

        name = self._parseFullIdentity(desc)
        # print "parse message ", name
        cls = None

        if cls is None:
            if self.ast.isMessageExist(name):
                self.error(desc, "type '%s' has been exist." % name)

            cls = MessageDescriptor(name)
            self.ast.addMessage(cls)

        self.matchNext('{', desc)

        token = self.nextToken()
        while token != None and token != '}':
            if token == ';':
                pass

            elif token == T_MESSAGE:
                self.parse_message(parent=cls)

            elif token == T_ENUM:
                self.parse_enum(parent=cls)

            elif token == T_OPTION:
                self.parse_option(cls)

            elif token in VALID_QUALIFIER_TOKENS:
                self._parseMessageVarField(cls, desc)

            elif token == T_MAP:
                self._parseMessageMapField(cls, desc)

            elif token == T_EXTENSIONS:
                self._parseExtensions(cls)

            elif token == T_RESERVED:
                self._parseReserved(cls)

            elif token == T_EXTEND:
                self.parse_extend(parent=cls)

            else:
                self.error(desc, "invalid token '%s'" % token2str(token))

            token = self.nextToken()

        self.matchToken(token, '}', desc)

    def _parseMessageVarField(self, cls, desc):
        token = self.tokenInfo.token

        varQualifier = token2str(token)
        varType = self._parseFullIdentity(desc)

        varName = self._parseIdentity(desc)

        self.matchNext('=', desc)

        self.matchNext(T_NUMBER, desc)
        varOrder = self.tokenInfo.value

        token = self.lookAhead()
        if token == '[':
            self._parseFiledOption(desc)

        self.matchNext(';', desc)
        cls.addMember(varOrder, varQualifier, varName, varType)

    def _parseFiledOption(self, desc):
        self.nextToken()  # ignore '['
        while True:
            self.matchNext(T_IDENTITY, desc)
            self.matchNext('=', desc)
            self.matchNext(VALID_VALUE_TOKENS, desc)

            token = self.nextToken()
            if token == ']':
                break

            self.matchToken(token, ',', desc)
        return

    def _parseRange(self, parent, desc):
        while True:
            self.matchNext(T_NUMBER, desc)
            litMin = self.tokenInfo.value
            litMax = None

            token = self.nextToken()
            if token == T_TO:
                token = self.nextToken()
                if token == T_NUMBER:
                    litMax = self.tokenInfo.value
                elif token == T_IDENTITY and self.tokenInfo.value == "max":
                    pass
                else:
                    self.error(desc, "invalid token '%s'" % token2str(token))

                token = self.nextToken()

            if token == ';':
                break

            self.matchToken(token, ',', desc)
        return

    def _parseFieldList(self, parent, desc):
        while True:
            self.matchNext(T_STRING, desc)

            token = self.nextToken()
            if token == ';':
                break

            self.matchToken(token, ',', desc)
        return

    def error(self, desc, msg):
        msg = "error: file '%s', line=%d, column=%d, %s: %s" % (
            self.fileName, self.tokenInfo.line, self.tokenInfo.column, desc, msg)
        raise ProtoException, msg

    def matchIdentity(self, token, desc):
        if not is_identity_token(token):
            self.error(desc, "identity expected, but '%s' was given" % token2str(token))

        return

    def _parseIdentity(self, desc):
        token = self.nextToken()
        self.matchIdentity(token, desc)
        return self.tokenInfo.value

    def _parseFullIdentity(self, desc):
        """
        解析一个变量的全名。bnf格式如：name = identity { '.' name }

        :param desc:当前要为什么类型的语句解析符号，用于出错时打印log 
        :return: 返回变量全名。如: xxx 或 xxx.yyy的形式
        """
        name = ""
        while True:
            name += self._parseIdentity(desc)

            token = self.lookAhead()
            if token != '.':
                break

            self.nextToken()
            name += '.'

        return name

    def parse_syntax(self):
        desc = "syntax"
        self.matchNext('=', desc)
        self.matchNext(T_STRING, desc)

        syntax = self.tokenInfo.value

        # if syntax != "proto2":
        #     self.error(desc, "only 'proto2' was supported. but '%s' was given", syntax)

        # self.fd.setSyntax(syntax)
        return

    def _parseTemplateArgs(self, desc):
        ''' 语法格式:
        template = '<' t_args '>'
        t_args = full_identity {',' t_args }
        '''
        ret = []

        while True:
            varType = self._parseFullIdentity(desc)
            ret.append(varType)

            token = self.lookAhead()
            if token == '>':
                break

            self.matchNext(',', desc)

        self.nextToken()  # ignore '>'

        if len(ret) == 0:
            self.error(desc, "template args is empty.")

        return ret

    def _parseTemplateArgs(self, desc):
        ''' 语法格式:
        template = '<' t_args '>'
        t_args = full_identity {',' t_args }
        '''
        ret = []

        while True:
            varType = self._parseFullIdentity(desc)
            ret.append(varType)

            token = self.lookAhead()
            if token == '>':
                break

            self.matchNext(',', desc)

        self.nextToken()  # ignore '>'

        if len(ret) == 0:
            self.error(desc, "template args is empty.")

        return ret

    def _parseMessageMapField(self, cls, desc):
        self.matchNext('<', desc)
        mapArgs = self._parseTemplateArgs(desc)
        # print "_parseMessageMapField",mapArgs
        varName = self._parseIdentity(desc)

        self.matchNext('=', desc)

        self.matchNext(T_NUMBER, desc)
        varOrder = self.tokenInfo.value

        self.matchNext(';', desc)

        cls.addMember(varOrder, "optional", varName, "map",mapArgs)
