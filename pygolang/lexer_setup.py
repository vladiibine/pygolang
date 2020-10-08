import contextlib

import ply.lex as lex

###
# names here are used via reflection.
# Don't just rename them, everything will break!

# Tokens
from .common_grammar import tokens

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQUALS = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'


def t_NUMBER(t):
    r"""\d+"""
    try:
        t.value = int(t.value)
    except ValueError:
        IO_CALLBACK.to_stdout("Integer value too large %d" % t.value)
        t.value = 0
    return t


# Ignored characters
t_ignore = " \t"


def t_newline(t):
    r"""\n+"""
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    IO_CALLBACK.to_stdout("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


IO_CALLBACK = None
# End of "DO NOT TOUCH" section
###


@contextlib.contextmanager
def build_lexer(io_callback):
    global IO_CALLBACK
    IO_CALLBACK = io_callback

    yield lex.lex()

    IO_CALLBACK = None
