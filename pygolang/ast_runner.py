import operator as py_operator

from pygolang import ast


OPERATOR_MAP = {
    '+': py_operator.add,
    '-': py_operator.sub,
    '/': py_operator.truediv,
    '*': py_operator.mul,
}


class Runner:
    def __init__(self, io, state):
        self.io = io
        # TODO -> access to this needs to be replaced with a call to a
        #  method which searches for variables in a list of scopes
        #  AND if it writes something, it writes in the first scope it gets
        self.state = state

    def run(self, code, scopes=None):
        value = None
        scopes = scopes or []

        if isinstance(code, ast.Root):
            if isinstance(code.value, ast.InterpreterStart):
                value = self.run_statement(code.value.value, scopes)
                if value is not None:
                    self.io.to_stdout(value)
        elif isinstance(code, ast.FuncBody):
            for stmt in code.statements:
                value = self.run(stmt, scopes)
                if isinstance(stmt, ast.Return):
                    break

        elif isinstance(code, ast.Operator):
            value = self.run_operator(code, scopes)

        elif isinstance(code, ast.Expression):
            value = self.run_expression(code, scopes)

        elif isinstance(code, ast.Leaf):
            value = code.value

        elif isinstance(code, ast.Return):
            value = self.run(code.value, scopes)

        return value

    def run_statement(self, stmt, scopes):
        result = None

        if isinstance(stmt, ast.Assignment):
            key = stmt.name
            value = self.run(stmt.value)

            # Global scope, until we implement per-something-else scope
            self.state[key] = value

        elif isinstance(stmt, ast.Func):
            self.state[stmt.name] = stmt

        elif isinstance(stmt, ast.Expression):
            result = self.run_expression(stmt, scopes)

        elif isinstance(stmt, ast.FuncCall):
            result = self.call_func(stmt)

        elif isinstance(stmt, ast.Statement):
            result = self.run_statement(stmt.value, scopes)

        return result

    def run_expression(self, exp, scopes):
        """
        :param list[dict] scopes:
        :return:
        """
        if isinstance(exp, ast.Leaf):
            return exp.value

        elif isinstance(exp, ast.Name):
            # TODO - replace global state with scopes
            return self.state[exp.value]

        elif isinstance(exp, ast.Operator):
            return self.run_operator(exp, scopes)

        elif isinstance(exp, ast.Expression):
            # we only know how to treat the NAME expression here
            if len(exp.children) == 1:
                if isinstance(exp.children[0], ast.Name):
                    return self.state[exp.children[0].value]

                elif isinstance(exp.children[0], ast.Leaf):
                    return exp.children[0].value

                elif isinstance(exp.children[1], ast.FuncCall):
                    return self.call_func(exp.children[1])

                return self.run_expression(exp.children[0], scopes)

    def run_operator(self, operator_expr, scopes):
        """
        :param ast.Operator operator_expr:
        :param list[dict] scopes:
        :return:
        """

        if len(operator_expr.args_list) == 2:
            operand1_exp, operand2_exp = operator_expr.args_list

            operand1 = self.run_expression(operand1_exp, scopes)
            operand2 = self.run_expression(operand2_exp, scopes)

            return OPERATOR_MAP[operator_expr.operator](operand1, operand2)

    def call_func(self, func_call):
        func = self.state[func_call.func_name]
        scope = {}

        # 1. match args to params
        # 2. put them in the scope
        # 3. run the code from its body as the list of instructions it contains
        # 4. return the result

        # 1.1. match args to params - first find out what the params are
        # param_types = [(n, t) for n, t in (func.params.token)]
        # Examples of signatures:
        # x int, y int, z int
        # x, y, z int, a, b, c int

        # if there's no previous token, we push a name
        # if name comes after name, we push a type
        # if name comes after comma, we push a name
        # TODO - move this logic in the ast.Function, during obj. construction
        param_names = []
        param_types = []
        prev_token = None
        for token in func.params.token:  # type: ply.lexer.LexToken
            if prev_token is None:
                param_names.append(token.value)
                prev_token = token
            elif token.type == 'NAME' and prev_token.type == 'NAME':
                param_types.extend([token.value] * (len(param_names) - len(param_types)))
                prev_token = token
            elif token.type == 'NAME' and prev_token.type == 'COMMA':
                param_names.append(token.value)
                prev_token = token
            else:
                prev_token = token  # handling commas

        params = zip(param_names, param_types)

        # 1.2. then put in scope the params with the values from the args
        for (pname, ptype), arg_abstrat_value in zip(params, func_call.args.arg_list):
            arg_value = self.run_expression(arg_abstrat_value, [scope])

            # TODO -> we don't check for types here, and we shouldn't
            #   What we should do is check types at parse time
            # 2. put the params in the scopt of the function
            scope[pname] = arg_value

        # 3. run the function
        result = self.run(func.body, scopes=[scope])

        return result
