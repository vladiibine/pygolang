import ply.yacc as yacc

###
# Do not just rename variables in the next section!
# They're used via reflection. Renaming them breaks everything
from ply.lex import LexToken

from pygolang import ast
from .common_grammar import tokens


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
        t[0] = ast.Root(ast.InterpreterStart(t[1]))

    def p_expression_1(self, t):
        """expression : NUMBER"""
        if t.slice[1].type == 'NUMBER':
            t.slice[0].value = ast.Number(t.slice[1].value)

    def p_expression_2(self, t):
        """expression : NAME LPAREN args_list RPAREN"""
        t[0] = ast.FuncCall(func_name=t[1], args=t[3])

    def p_expression_3(self, t):
        """expression : NAME LPAREN RPAREN"""
        t[0] = ast.FuncCall(func_name=t[1], args=ast.FuncArguments([]))

    def p_args_list(self, t):
        """args_list : expression
                    | expression COMMA
                    | args_list COMMA expression
        """
        t.slice[0].value = ast.FuncArguments(
            # t.slice[1:]
            # How do I know if these are literals, names or expressions?
            # ...cuz the definition says they're all expressions I guess
            [ast.Expression([elem.value]) for elem in t.slice[1:]]
        )

    def p_assignment_statement(self, t):
        """assignment_statement : NAME EQUALS expression"""
        t[0] = ast.Assignment(t[1], t[3])
        # self.program_state[t[1]] = t[3]

    def p_expression_statement(self, t):
        """expression_statement : expression"""
        # This works for values
        t[0] = ast.Statement(t.slice[1].value)
        # t.slice[0].value = t.slice[1].value

    def p_func_statement(self, t):
        """func_statement : FUNC NAME LPAREN func_params RPAREN func_return_type LBRACE func_body RBRACE """
        self.program_state[t[2]] = ast.Func(
            name=t.slice[2].value,
            params=t.slice[4].value,
            return_type=t.slice[6].value,
            body=t.slice[8].value)

    def p_func_params(self, t):
        """func_params :
                        | NAME NAME
                        | NAME COMMA func_params
                        | func_params COMMA func_params
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
        t[0] = ast.Statement(t[1])

    def p_func_body(self, t):
        """func_body : assignment_statement
                    | return_statement
                    | expression_statement
                    | func_body func_body
        """
        t.slice[0].value = ast.FuncBody([e.value for e in t.slice[1:]])

    def p_return_statement(self, t):
        """return_statement : RETURN expression"""
        t.slice[0].value = ast.Return(t.slice[2].value)


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
        operator_chars = {'+', '-', '/', '*'}

        if t[2] in operator_chars:
            t[0] = ast.Operator(t[2], [t[1], t[3]])
            return

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

    def p_expression_name(self, t):
        """expression : NAME"""
        # t.slice[0].value = self.program_state[t.slice[1].value]

        if len(t.slice) == 2:
            if isinstance(t.slice[1], LexToken):
                if t.slice[1].type == 'NAME':
                    expression_node = ast.Name(t.slice[1].value)

                    t.slice[0].value = ast.Expression([expression_node])

    def p_error(self, t):
        self.io_callback.to_stderr("pygo: Syntax error at '%s'" % t.value)
