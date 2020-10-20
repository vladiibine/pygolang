import ply.yacc as yacc

from ply.lex import LexToken

from pygolang import ast
from pygolang.errors import PyGoGrammarError, PyGoConsoleLogoffError
from . import common_grammar
from .common_grammar import OPERATORS

TYPE_MAP = {
    'BOOL': ast.BoolType,
    'INT': ast.IntType,
    'STRING': ast.StringType,
}


class PyGoParser:
    tokens = common_grammar.tokens
    precedence = (
        # Precedence -> up=low; down=HIGH!
        ('left', OPERATORS.BOOLOR.value),
        ('left', OPERATORS.BOOLAND.value),
        ('left', OPERATORS.BOOLEQUALS.value, OPERATORS.BOOLNOTEQUALS.value),
        ('left', OPERATORS.PLUS.value, OPERATORS.MINUS.value, ),
        ('left', OPERATORS.TIMES.value, OPERATORS.DIVIDE.value),
        ('left', OPERATORS.NOT.value),
        # ('left', 'MODULO'),
        # ('right', 'UMINUS'),
    )

    start = 'interpreter_start'

    def __init__(self, io, state):
        self.io_callback = io
        self.program_state = state

        self.type_scope_stack = ast.TypeScopeStack()
        self.parser = yacc.yacc(module=self)

    def parse(self, *a, **kw):
        return self.parser.parse(*a, **kw)

    def p_interpreter_start(self, t):
        """interpreter_start : statement"""
        t[0] = ast.Root(ast.InterpreterStart(t[1]))

    def p_expression_int(self, t):
        """expression : INT"""
        if t.slice[1].type == 'INT':
            t.slice[0].value = ast.Int(t.slice[1].value)

    def p_expression_string(self, t):
        """expression : STRING"""
        t[0] = ast.String(t[1])

    def p_expression_func_call(self, t):
        """expression : NAME LPAREN args_list RPAREN"""
        current_scope = self.type_scope_stack.get_current_scope()
        func_return_type = current_scope.get_variable_type(t[1])

        t[0] = ast.FuncCall(func_name=t[1], args=t[3], type=func_return_type)

    def p_expression_3(self, t):
        """expression : NAME LPAREN RPAREN"""
        current_scope = self.type_scope_stack.get_current_scope()
        func_type = current_scope.get_variable_type(t[1])  # type: ast.Type

        t[0] = ast.FuncCall(
            func_name=t[1], args=ast.FuncArguments([]),
            type=func_type.rtype
        )

    def p_expression_4(self, t):
        """expression : TRUE
                        | FALSE
        """
        if t.slice[1].type == 'TRUE':
            t[0] = ast.BoolLiteralTrue

        else:
            t[0] = ast.BoolLiteralFalse
        # t[0] = ast.Bool(t[1])

    def p_args_list(self, t):
        """args_list : expression
                    | args_list COMMA
                    | args_list COMMA args_list
        """
        t.slice[0].value = ast.FuncArguments(
            # t.slice[1:]
            # How do I know if these are literals, names or expressions?
            # ...cuz the definition says they're all expressions I guess
            [
                ast.Expression(
                    child=elem.value,
                    type_scope=self.type_scope_stack.get_current_scope()
                )
                for elem in t.slice[1:] if elem.type != 'COMMA'
            ]
        )

    def p_declaration_statement(self, t):
        """declaration_statement : VAR NAME type_declaration EQUALS expression
                                | VAR NAME type_declaration
                                | NAME WALRUS expression
        """
        if len(t.slice) == 6:
            t[0] = ast.Declaration(
                name=t[2],
                type=t[3],
                value=t[5],
                type_scope=self.type_scope_stack.get_current_scope()
            )

        elif len(t.slice) == 4 and t.slice[1].type == common_grammar.KEYWORDS.VAR.value:
            t[0] = ast.Declaration(
                name=t[2],
                type=t[3],
                type_scope=self.type_scope_stack.get_current_scope()
            )
        elif len(t.slice) == 4 and t.slice[2].type == common_grammar.OPERATORS.WALRUS.value:
            t[0] = ast.Declaration(
                name=t[1],
                type=t[3].type,
                value=t[3],
                type_scope=self.type_scope_stack.get_current_scope(),
            )

    def p_type_declaration(self, t):
        """type_declaration : BOOL
                            | INT
                            | STRING
        """
        try:
            t[0] = TYPE_MAP[t.slice[1].type]
        except KeyError:
            raise PyGoGrammarError(
                f"The type specified is not implemented: {t.slice[1].type}")

    def p_assignment_statement(self, t):
        """assignment_statement : NAME EQUALS expression"""
        t[0] = ast.Assignment(t[1], t[3], type_scope=self.type_scope_stack.get_current_scope())
        # self.program_state[t[1]] = t[3]

    def p_expression_statement(self, t):
        """expression_statement : expression"""
        # This works for values
        t[0] = ast.Statement(t.slice[1].value)
        # t.slice[0].value = t.slice[1].value

    # def p_func_statement(self, t):
    #     """func_statement : FUNC NAME LPAREN func_params RPAREN func_return_type new_scope_start func_body new_scope_end """
    #     t[0] = ast.FuncCreation(
    #         name=t.slice[2].value,
    #         params=t.slice[4].value,
    #         return_type=t.slice[6].value,
    #         body=t.slice[8].value)
        # self.program_state[t[2]] = ast.FuncCreation(
        #     name=t.slice[2].value,
        #     params=t.slice[4].value,
        #     return_type=t.slice[6].value,
        #     body=t.slice[8].value)

    def p_func_statement(self, t):
        """func_statement : func func_signature LBRACE func_body new_scope_end"""

        func_creation = ast.FuncCreation(
            name=t[2][0], params=t[2][1], return_type=t[2][2], body=t[4])
        t[0] = func_creation

        scope = self.type_scope_stack.get_current_scope()
        scope.declare_variable_type(
            func_creation.name,
            func_creation.type
        )

    def p_func(self, t):
        """func : FUNC"""
        # Dummy rule, created only so a new scope will be created
        self.type_scope_stack.create_scope()

    def p_func_signature(self, t):
        """func_signature : NAME LPAREN func_params RPAREN func_return_type"""
        # Pass the values to the p_func_statement handler
        func_name = t[1]  # type: str
        func_params = t[3]  # type: ast.FuncParams
        func_rtype = t[5]  # type: ast.FuncReturnType

        t[0] = [func_name, func_params, func_rtype]  # name, params, rtype

        # Declare the function's parameters in its type scope
        param_types = ast.FuncCreation.get_params_and_types_static(func_params.params)
        scope = self.type_scope_stack.get_current_scope()
        for param, type_ in param_types:
            scope.declare_variable_type(param, type_)

    def p_new_scope_start(self, t):
        """new_scope_start : LBRACE"""
        # Dummy rule, used only to mark the beginning of a new lexical scope
        self.type_scope_stack.create_scope()

    def p_new_scope_end(self, t):
        """new_scope_end : RBRACE"""
        # Dummy rule, used only to mark the end of a new lexical scope
        self.type_scope_stack.pop_scope()

    def p_func_params(self, t):
        """func_params :
                        | NAME type_declaration
                        | NAME COMMA func_params
                        | func_params COMMA func_params
        """
        # TODO -> BUG, this matches `<empty>, <empty>, ...`
        t.slice[0].value = ast.FuncParams(t.slice[1:])

    def p_func_return_type(self, t):
        """func_return_type : type_declaration """
        t.slice[0].value = t.slice[1:]

    def p_statement(self, t):
        """statement : func_statement
                    | assignment_statement
                    | declaration_statement
                    | expression_statement
                    | conditional_statement
        """
        t.slice[0].value = ast.Statement(t.slice[1].value)

    def p_conditional_statement_1(self, t):
        """conditional_statement : IF expression new_scope_start block new_scope_end"""
        t[0] = ast.Conditional(
            [(t[2], t[4])],
            [],
            self.type_scope_stack.get_current_scope()
        )

    def p_conditional_statement_2(self, t):
        """conditional_statement : conditional_statement ELSE conditional_statement"""
        # inline the child conditionals into the current one:
        t[0] = ast.Conditional(
                t[1].expression_block_pairs + t[3].expression_block_pairs,
                final_block=t[1].final_block or t[3].final_block,
                scope=self.type_scope_stack.get_current_scope(),
            )

    def p_conditional_statement_3(self, t):
        """conditional_statement : conditional_statement ELSE new_scope_start block new_scope_end"""

        # length of t.slice:
        # if expr { ... } = 1 5
        # if expr { ... } else { ... } = 1 5 4
        # if expr { ... } else if expr { ... } else if expr { ... } = 1 5 1 5 1 5
        # if expr { ... } else if expr { ... } else if expr { ... } else if expr { ... } = 1 5 1 5 1 5
        # if expr { ... } else if expr { ... } else if expr { ... } else if expr { ... } else if expr { ... } = 1 5 1 5 1 5 1 5
        # if expr { ... } else if expr { ... } else if expr { ... } else if expr { ... } else if expr { ... } else { ... } = 1 5 1 5 1 5 1 5 4
        # 1 5 (=6)
        # 1 5 1 5 (=12)
        # 1 5 1 5 1 5 (=18...24, 30, 36, 42, 48
        # 1 5 (1 5)* (4)?
        # out of which, the expressions will be on opsitions 2, 8, 14, 20, 26: 2 + 6*N
        # and the blocks will be on positions: 4, 10, 16, 22, 28, 32: 4 + 6*N (+4)
        previous_conditional = t[1]  # type: ast.Conditional
        t[0] = ast.Conditional(
            previous_conditional.expression_block_pairs,
            final_block=t[4],
            scope=self.type_scope_stack.get_current_scope()
        )

    def p_block(self, t):
        """block : statement
                | block statement
        """
        t[0] = ast.Block(t[1:])

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

    def p_expression_group(self, t):
        """expression : LPAREN expression RPAREN"""
        # This is so we can group things with parentheses
        t[0] = t[2]

    def p_expression_binop(self, t):
        """expression : expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | expression DIVIDE expression
                      | expression MODULO expression
                      | expression BOOLEQUALS expression
                      | expression BOOLNOTEQUALS expression
                      | expression GREATER expression
                      | expression LESSER expression
                      | expression GREATEREQ expression
                      | expression LESSEREQ expression
                      | expression BOOLAND expression
                      | expression BOOLOR expression
                      | NOT expression
        """
        # operator_chars = {'+', '-', '/', '*', '==', '!=', '>', '<', '>=', '<=', '%'}

        # if t[2] in operator_chars:
        if len(t.slice) == 4:
            t[0] = ast.Operator(t[2], t.slice[2].type, [t[1], t[3]])
        elif len(t.slice) == 3:
            t[0] = ast.Operator(t[1], t.slice[1].type, [t[2]])

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

        """
        When should an expression's value be determined?
        1. It can be determined, for literals, at parse-time 
        2. For names, it should be determined before run-time
        3. Function calls it should be determined before run-time
        4. Operators, again, before run-time

        So the plan is to
        1. Have the parser determine the type of literals
        2. How to have the parser determine the type of names?
            2.1. Solution: TypeScopes. See Expression.determine_type
        3. Functions -> easy; type is specified
        4. Operators -> easy; table of types
        
        So our problem really is determining the types of names.
        For this we kind of need scopes before run-time, or smth.
        1. We can use a stack of scopes(dicts)
        2. Every time we exit a function, we should do a type check
        3. Every time exit a block, we should do a type check
        2. Every time we create a function, we should have all expressions(?) 
            in it be checked for value matches
            
        What situations are there when we care about value match?
        1. return statements
        2. variable assignments
        3. walrus declaration
        3. operator usage
        """

        if len(t.slice) == 2:
            if isinstance(t.slice[1], LexToken):
                if t.slice[1].type == 'NAME':
                    expression_node = ast.Name(t.slice[1].value)

                    t.slice[0].value = ast.Expression(
                        expression_node,
                        self.type_scope_stack.get_current_scope()
                    )

    def p_error(self, t):
        if t and hasattr(t, 'value'):
            self.io_callback.to_stderr("pygo: Syntax error at '%s'" % t.value)
        raise PyGoConsoleLogoffError
