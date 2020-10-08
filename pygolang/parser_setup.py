import contextlib

import ply.yacc as yacc

###
# Do not just rename variables in the next section!
# They're used via reflection. Renaming them breaks everything
from contextlib2 import contextmanager

from .common_grammar import tokens

precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('right', 'UMINUS'),
)


def p_statement_assign(t):
    """statement : NAME EQUALS expression"""
    PROGRAM_STATE[t[1]] = t[3]


def p_statement_expr(t):
    """statement : expression"""
    IO_CALLBACK.to_stdout(t[1])


def p_expression_binop(t):
    """expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression"""
    if t[2] == '+':
        t[0] = t[1] + t[3]
    elif t[2] == '-':
        t[0] = t[1] - t[3]
    elif t[2] == '*':
        t[0] = t[1] * t[3]
    elif t[2] == '/':
        t[0] = t[1] / t[3]


def p_expression_uminus(t):
    """expression : MINUS expression %prec UMINUS"""
    t[0] = -t[2]


def p_expression_group(t):
    """expression : LPAREN expression RPAREN"""
    t[0] = t[2]


def p_expression_number(t):
    """expression : NUMBER"""
    t[0] = t[1]


def p_expression_name(t):
    """expression : NAME"""
    try:
        t[0] = PROGRAM_STATE[t[1]]
    except LookupError:
        IO_CALLBACK.to_stdout("Undefined name '%s'" % t[1])
        t[0] = 0


def p_error(t):
    IO_CALLBACK.to_stdout("Syntax error at '%s'" % t.value)


IO_CALLBACK = None
PROGRAM_STATE = None
#
# THE END of the "DO NOT TOUCH" section
###


@contextlib.contextmanager
def build_parser(io, state):
    global IO_CALLBACK
    IO_CALLBACK = io

    global PROGRAM_STATE
    PROGRAM_STATE = state

    yield yacc.yacc()

    PROGRAM_STATE = None
    IO_CALLBACK = None
