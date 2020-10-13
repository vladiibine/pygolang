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
        """

        :param io:
        :param dict|ast.ModuleScope state: the program's starting state
        """
        self.io = io
        # TODO -> access to this needs to be replaced with a call to a
        #  method which searches for variables in a list of scopes
        #  AND if it writes something, it writes in the first scope it gets
        if isinstance(state, dict):
            self.state = ast.ModuleScope(state)
        elif isinstance(state, ast.ModuleScope):
            self.state = state
        else:
            raise Exception(
                "The program's state should be a module scope or a dict")

    def run(self, code, scopes=None):
        value = None
        scopes = scopes or [self.state]

        if isinstance(code, ast.Root):
            value = self.run(code.value, scopes)

        elif isinstance(code, ast.InterpreterStart):
            value = self.run(code.value, scopes)
            if value is not None:
                self.io.to_stdout(value)

        elif isinstance(code, ast.FuncBody):
            for stmt in code.statements:
                value = self.run(stmt, scopes)
                if isinstance(stmt, ast.Return):
                    break

        elif isinstance(code, ast.Assignment):
            # 1. see if the variable is declared in the current scope
            # 2. if so, set it
            # 3. TODO ERROR: var was not declared: the parser should have
            #       raised an error, because that's not allowed
            key = code.name
            assigned_value = self.run(code.value, scopes)

            # Global scope, until we implement per-something-else scope
            self.set_in_scopes(key, assigned_value, scopes)

        elif isinstance(code, ast.Func):
            self.set_in_scopes(code.name, code, scopes)

        # return result

        elif isinstance(code, ast.Name):
            # TODO - replace global state with scopes
            # return self.state[exp.value]
            return self.find_in_scopes(code.value, scopes)

        elif isinstance(code, ast.Operator):
            value = self.run_operator(code, scopes)

        elif isinstance(code, ast.Leaf):
            value = code.value

        elif isinstance(code, ast.Expression):
            # we only know how to treat the NAME expression here
            if len(code.children) == 1:
                if isinstance(code.children[0], ast.Name):
                    # return self.state[code.children[0].value]
                    return self.find_in_scopes(code.children[0].value, scopes)

                elif isinstance(code.children[0], ast.Leaf):
                    return code.children[0].value

                elif isinstance(code.children[0], ast.FuncCall):
                    return self.call_func(code.children[0], scopes)

                return self.run(code.children[0], scopes)

        elif isinstance(code, ast.Return):
            value = self.run(code.value, scopes)

        elif isinstance(code, ast.FuncCall):
            value = self.call_func(code, scopes)

        elif isinstance(code, ast.Statement):
            value = self.run(code.value, scopes)

        return value

    def set_in_scopes(self, name, value, scopes):
        scopes[0][name] = value

    def find_in_scopes(self, name, scopes):
        """
        :param str name:
        :param list[dict] scopes:
        :return:
        """
        for scope in scopes:
            # Function scopes should be skipped when looking for variables
            # ..this might get more complicated when creating
            # if isinstance(scope, ast.FuncScope):
            #     continue
            if name in scope:
                return scope[name]

        # well... should raise an error if the name is not in any scope
        #  BUT it's really the job of the parser to prevent this situation

    def run_operator(self, operator_expr, scopes):
        """
        :param ast.Operator operator_expr:
        :param list[dict] scopes:
        :return:
        """

        if len(operator_expr.args_list) == 2:
            operand1_exp, operand2_exp = operator_expr.args_list

            operand1 = self.run(operand1_exp, scopes)
            operand2 = self.run(operand2_exp, scopes)

            return OPERATOR_MAP[operator_expr.operator](operand1, operand2)

    def call_func(self, func_call, scopes):
        # 1. find the function's parameters
        # 2. match them against the arguments
        # 3. set the parameters as variables in the newly created scope
        # 4. run the function's body using the new and previous scopes
        # 5. profit!
        scopes = scopes or []
        scopes.insert(0, ast.FuncScope({}))

        func = self.find_in_scopes(func_call.func_name, scopes)  # type: ast.Func

        params = func.get_params_and_types()

        # flatten function arguments
        flat_arguments = []
        for func_args in func_call.args.arg_list if func_call.args else []:
            for child in func_args.children:
                if isinstance(child, ast.FuncArguments):
                    for child_expr in child.arg_list:
                        flat_arguments.append(child_expr)
                else:
                    flat_arguments.append(child)

        # set in the new function scope the arguments as variables
        for (pname, ptype), arg_abstrat_value in zip(params, flat_arguments):
            arg_value = self.run(arg_abstrat_value, scopes)

            # TODO -> we don't check for types here, and we shouldn't
            #   What we should do is check types at parse time
            scopes[0][pname] = arg_value

        result = self.run(func.body, scopes=scopes)

        # Don't forget to destroy the created scope!
        scopes.pop(0)

        return result


