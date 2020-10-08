import sys

###
# parsing section,
# these names are used via reflection, don't change them,
# and don't change their order
# from ply import yacc, lex
import ply.yacc as yacc

# !!!!!!! STATE  KEPT  AT  MODULE-LEVEL
# State(global vars). TODO: Remove this after making the code work
from . import lexer_setup
from .common_grammar import tokens

PROGRAM_STATE = None
IO_CALLBACK = None  # type: IO


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

# end of parsing section


class PyLangRuntimeError(Exception):
    pass


class PyLangValueError(PyLangRuntimeError):
    pass


class StopPyGoLangInterpreterError(Exception):
    pass


class IO:
    def __init__(self, stdout=None, stderr=None, stdin=None):
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr
        self.stdin = stdin or sys.stdin
        # ...add all file descriptors here
        # for all files, for all sockets, for everything that's IO

    def to_stdout(self, stuff):
        self.stdout.write(str(stuff))
        self.stdout.flush()

    def from_stdin(self):
        return self.stdin.readline().lstrip('\n')

    def interpreter_prompt(self):
        self.to_stdout("pygo> ")


def main(io=IO(), program_state=None):

    # Weird code, I know. The parser relies on reflection for finding
    # handler function names. It loads stuff from the global variables.
    # The module used for loading stuff I ASSUME is the one where the lexer
    # and parser are initialized.
    global IO_CALLBACK
    global PROGRAM_STATE

    IO_CALLBACK = io
    PROGRAM_STATE = program_state if program_state is not None else {}

    lexer = lexer_setup.build_lexer(io)
    parser = yacc.yacc()

    try:
        while True:
            try:
                io.interpreter_prompt()
                instruction_set = io.from_stdin()

                parser.parse(instruction_set)
                io.to_stdout('\n')
                # io.to_stdout("You wrote:\n{}".format(instruction_set))

            except StopPyGoLangInterpreterError:
                break

            except PyLangRuntimeError as err:
                io.to_stdout("Error: {}".format(err))
    finally:
        IO_CALLBACK = None
        PROGRAM_STATE = None


if __name__ == '__main__':
    main()
