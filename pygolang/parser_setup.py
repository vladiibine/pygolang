import ply.yacc as yacc

###
# Do not just rename variables in the next section!
# They're used via reflection. Renaming them breaks everything
from pygolang import ast
from .common_grammar import tokens


class FunctionBuilder:
    """This class exists because the ply library is missing features.

    The production rules don't return anything that the parser remembers.
    They're called only for their side-effects, but they can't have side
    effects on anything the parser does, so then we need to keep track of
    parser events (such as when it parsed parts of a function definition)
    """
    params = None
    body = None
    return_type = None

    @classmethod
    def clear(cls):
        cls.params = cls.body = cls.return_type = None

    @classmethod
    def is_in_progress(cls):
        return cls.params or cls.body or cls.return_type

#
# THE END of the "DO NOT TOUCH" section
###


class PyGoParser:
    tokens = tokens
    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        # ('right', 'UMINUS'),
    )

    start = 'interpreter_start'

    def __init__(self, io, state):
        self.io_callback = io
        self.program_state = state

        self.parser = yacc.yacc(module=self)

    def parse(self, *a, **kw):
        return self.parser.parse(*a, **kw)

    def p_interpreter_start(self, t):
        """interpreter_start : statement"""
        return t

    def p_expression_1(self, t):
        """expression : NUMBER"""
        t.slice[0].value = t.slice[1:]

    def p_expression_2(self, t):
        """expression : NAME LPAREN args_list RPAREN"""
        # Do stuff like call a function
        # ...so actually run go code! ....ooooh man, I'm excited! :D
        func = self.program_state[t.slice[1].value]

        value = None
        for instruction in func.body:
            if instruction.type == 'return_statement':
                # Expecting a list, but this is going to be
                # buggy, as I haven't decided where I use lists
                # and where scalar elements
                # ...oh well, lots of test will force me to
                # decide
                # t.slice[0].value = instruction.value
                value = instruction.value[0].value
                break

        t.slice[0].value = value

    def p_args_list(self, t):
        """args_list : expression
                    | expression COMMA
                    | args_list COMMA expression
        """
        t.slice[0].value = ast.FuncArguments(t.slice[1:])

    def p_assignment_statement(self, t):
        """assignment_statement : NAME EQUALS expression"""
        self.program_state[t[1]] = t[3]

    def p_expression_statement(self, t):
        """expression_statement : expression"""
        t.slice[0].value = t.slice[1].value

    def p_func_statement(self, t):
        """func_statement : FUNC NAME LPAREN func_params RPAREN func_return_type LBRACE func_body RBRACE """
        self.program_state[t[2]] = ast.Func(
            args=t.slice[4].value,
            return_type=t.slice[6].value,
            body=t.slice[8].value)

    def p_func_params(self, t):
        """func_params : NAME NAME
                        | NAME COMMA func_params
                        | func_params func_params
        """
        t.slice[0].value = ast.FuncParams(t.slice[1:])

    def p_func_return_type(self, t):
        """func_return_type : NAME """
        t.slice[0].value = t.slice[1:]

    def p_statement(self, t):
        """statement : func_statement
                    | assignment_statement
                    | expression_statement
        """
        return t


    def p_func_body(self, t):
        """func_body : assignment_statement
                    | return_statement
                    | expression_statement
                    | func_body func_body
        """
        t.slice[0].value = t.slice[1:]

    def p_return_statement(self, t):
        """return_statement : RETURN expression"""
        t.slice[0].value = t.slice[2].value
        return t


    # def p_compound_statement(t):
    #     """compound_statement : return_statement
    #                             | compound_statement return_statement
    #     """
    #     pass


    # def p_statement_return_statement(t):
    #     """statement : RETURN expression"""


    def p_expression_binop(self, t):
        """expression : expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | expression DIVIDE expression"""

        if t[2] == '+':
            t[0] = t[1][0].value + t[3][0].value
        elif t[2] == '-':
            t[0] = t[1][0].value - t[3][0].value
        elif t[2] == '*':
            t[0] = t[1][0].value * t[3][0].value
        elif t[2] == '/':
            t[0] = t[1][0].value / t[3][0].value
    #
    #
    # def p_expression_uminus(t):
    #     """expression : MINUS expression %prec UMINUS"""
    #     t[0] = -t[2]
    #
    #
    # def p_expression_group(t):
    #     """expression : LPAREN expression RPAREN"""
    #     t[0] = t[2]
    #
    #
    # def p_expression_number(t):
    #     """expression : NUMBER"""
    #     t[0] = t[1]
    #
    #
    # def p_expression_name(t):
    #     """expression : NAME"""
    #     try:
    #         t[0] = PROGRAM_STATE[t[1]]
    #     except LookupError:
    #         IO_CALLBACK.to_stderr("pygo: Undefined name '%s'" % t[1])
    #         t[0] = 0

    def p_error(self, t):
        self.io_callback.to_stderr("pygo: Syntax error at '%s'" % t.value)
