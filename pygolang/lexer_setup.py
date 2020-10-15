import ply.lex as lex

# Tokens
from .common_grammar import tokens, keywords_tuple


class PyGoLexer:
    ###
    # names here are used via reflection.
    # Don't just rename them, everything will break!
    tokens = tokens
    keywords = keywords_tuple

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_EQUALS = r'='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_COMMA = r','

    # Ignored characters
    t_ignore = " \t"

    def __init__(self, io_callback, type_scope_stack=None):
        """

        :param pygolang.io_callback.IO io_callback: Need this parameter
            to signal the creation of a new lexical scope when a "{" is reached
            Q: Do all situations where a "{" is read mark the beginning of
                a new lexical scope?
            A: I don't know any which don't
                >> UPDATE -> there might be situations, like with the
                interfaces, where we don't really mark new scopes....
                ..Ok, so I'll define some special parser rules for this
        :param pygolang.ast.TypeScopeStack type_scope_stack:
        """
        self.io_callback = io_callback
        self.lexer = self.build_lexer()
        # self.type_scope_stack = type_scope_stack

    def t_WALRUS(self, t):
        r""":="""
        return t

    def t_NAME(self, t):
        r"""[a-zA-Z_][a-zA-Z0-9_]*"""
        if t.value.upper() in keywords_tuple:
            t.type = t.value.upper()

        return t

    def t_TYPE(self, t):
        r"""[a-zA-Z_][a-zA-Z0-9_]*"""
        return t

    def t_INT(self, t):
        r"""\d+"""
        try:
            t.value = int(t.value)
        except ValueError:
            self.io_callback.to_stdout("Integer value too large %d" % t.value)
            t.value = 0
        return t

    def t_newline(self, t):
        r"""\n+"""
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        self.io_callback.to_stdout("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def build_lexer(self):
        return lex.lex(module=self)
