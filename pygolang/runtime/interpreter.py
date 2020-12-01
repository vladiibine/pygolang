from pygolang.runtime import namespaces
from pygolang import ast
from pygolang.runtime.importer import Importer


class Interpreter:
    def __init__(self, side_effects, state, package_name='main', importer=None):
        """

        :param side_effects:
        :param pygolang.runtime.namespaces.GlobalNamespace state: the
            program's starting state
        """
        self.side_effects = side_effects
        self.importer = importer or Importer(side_effects)
        self.scope_stack = namespaces.ScopeStack(state, package_name)

    def run(self, code):
        value = None

        if isinstance(code, ast.Root):
            for s in code.statements:
                value = self.run(s)  # Root

        elif isinstance(code, ast.InterpreterStart):
            for stmt in code.statements:
                value = self.run(stmt)

                # value = self.run(code.statements, scopes)  # InterpreterStart
                if value is not None:
                    self.side_effects.to_stdout(value.to_pygo_repr())

        elif isinstance(code, ast.StdlibImport):
            pass

        elif isinstance(code, ast.GopathImport):
            # There used to be code here which had to do with actually parsing
            # and importing files. That's wrong. Python would do that, but not
            # golang. In golang, at this point, we'd have a fully parsed
            # dependency package. This package would expose all variables
            # it exports.
            # In the runner, we'd merely make the exported variables reachable
            # from this module's scope
            code

            # 0. TODO -> Determine the import path. Will be useful for when
            #     importing other packages, and for displaying errors like
            #     go does. Go displays all the paths where it looked for
            #     packages, looking at env vars like $GOPATH and $GOROOT
            # 1. find the imported module
            # 2. import it
            # 3. get a list of (key, value) pairs
            # 4. add the keys/values to the current namespace

            # Try to import from the builtin modules
            # new_variables = []
            # new_variables.extend(
            #     self.importer.import_from_stdlib(code.import_str))
            # if new_variables:
            #     for qualified_name, obj_type, obj in new_variables:
            #         self.declare_in_scopes(qualified_name, obj_type, scopes)
            #         self.set_in_scopes(qualified_name, obj, scopes)
            #     return

            # TODO -> imports should not be done at run-time, but previously,
            #  during or right after parsing
            # found_files = False
            # for source in self.importer.import_from_gopath(code.import_str):
            #     found_files = True
            #     pass
            #
            # if found_files:
            #     return

            # new_variables.extend(
            #     self.importer.import_from_modules(code.import_str))
            # if new_variables:
            #     # yes, the code below is duplicated. Is it really worth
            #     # creating a method? don't think so
            #     for qualified_name, obj_type, obj in new_variables:
            #         self.declare_in_scopes(qualified_name, obj_type, scopes)
            #         self.set_in_scopes(qualified_name, obj, scopes)
            #     return

            # self.side_effects.to_stderr(
            #     f'cannot find package "{code.import_str}" in any of'
            # )

        elif isinstance(code, ast.Block):
            for stmt in code.statements:
                # scopes.insert(0, ast.BlockRuntimeScope({}))
                self.scope_stack.push_block_scope()
                self.run(stmt)  # Block
                # scopes.pop(0)
                self.scope_stack.pop()

        elif isinstance(code, ast.Conditional):
            # 1. iterate through the expression/block pairs
            # 2. evaluate the truth value of conditions
            # 3. at the first true condition, we evaluate the block
            # 4. if we haven't executed any of the blocks AND there's a final
            #      block, we evaluate that
            for expression, block in code.expression_block_pairs:
                expression_value = self.run(expression)  # Conditional, exp

                # Interesting! In go, there's no true-ish value.
                # Only true/false is expected, nothing else will work
                if expression_value == ast.BoolLiteralTrue:
                    self.run(block)  # Conditional, block
                    break

            else:
                # This executes when no expression was true-ish
                self.run(code.final_block)  # Conditional, final block

        elif isinstance(code, ast.FuncBody):
            for stmt in code.statements:
                value = self.run(stmt)  # FuncBody
                if isinstance(stmt, ast.Return):
                    break

        elif isinstance(code, ast.Declaration):
            key = code.name
            # value = code.value if code.value is ast.NotSet else self.run(code.value)
            type_ = code.type

            # TODO - at runtime, declarations should be replaced with
            #  assignments of the type's empty value. Type info doesn't need
            #  to be persisted at run-time, assuming all type checks have been
            #  done before run-time
            self.scope_stack.declare_in_scopes(key, type_)
            if code.value is not ast.ValueNotSet:
                assigned_value = self.run(code.value)  #
                try:
                    self.scope_stack.set_in_scopes(key, assigned_value)
                except Exception as err:
                    raise err


        elif isinstance(code, ast.Assignment):
            # 1. see if the variable is declared in the current scope
            # 2. if so, set it
            # 3. TODO ERROR: var was not declared: the parser should have
            #       raised an error, because that's not allowed
            key = code.name
            # self.set_in_scopes(key, ass)
            # if self.can_assign_in_scopes(key, scopes):
            assigned_value = self.run(code.value)  # Assignment
            self.scope_stack.set_in_scopes(key[0], assigned_value)
            #
            #     # Global scope, until we implement per-something-else scope
            #     self.set_in_scopes(key, assigned_value, scopes)
            # else:
            #     raise PyGoGrammarError(f"Can't assign value to {key}!")

        elif isinstance(code, ast.FuncCreation):
            self.scope_stack.declare_in_scopes(
                key=code.name,
                type_=ast.FuncCreation.get_func_type(code.params, code.return_type),
            )
            self.scope_stack.set_in_scopes(code.name, code)

        # return result

        elif isinstance(code, ast.Name):
            value = self.scope_stack.find_in_scopes(code.get_qualified_name())  # Name

        elif isinstance(code, ast.Operator):
            value = self.run_operator(code)  # Operator

        elif isinstance(code, ast.Value):
            value = code  # Value

        elif isinstance(code, ast.Expression):
            value = self.run(code.child)  # Expression

        elif isinstance(code, ast.Return):
            value = self.run(code.value)  # Return

        elif isinstance(code, ast.FuncCall):
            value = self.call_func(code)  # FuncCall

        elif isinstance(code, ast.Statement):
            value = self.run(code.value)  # Statement

        return value

    def run_operator(self, operator_expr):
        """
        :param ast.Operator operator_expr:
        :return:
        """
        operands = [
            self.run(operand_exp)
            for operand_exp in operator_expr.args_list
        ]
        result = operator_expr.operator_pyfunc(*operands)
        return result

    def call_native_func(self, func, scope):
        """
        :param ast.NativeFunction func:
        :param dict[str,object] scope:
        :return:
        """
        result = func.call(self.side_effects, scope)
        return result

    def call_func(self, func_call):
        # 1. find the function's parameters
        # 2. match them against the arguments
        # 3. set the parameters as variables in the newly created scope
        # 4. run the function's body using the new and previous scopes
        # 5. profit!
        self.scope_stack.push_function_scope()

        # func = self.find_in_scopes(func_call.func_name.get_qualified_name(), scopes)  # type: ast.Func
        func = self.scope_stack.find_in_scopes(func_call.func_name.get_qualified_name())

        # This is not necessary for native functions atm. They're just called
        # with their arguments, they don't need the scopes, as they don't
        # interact with normal variables
        new_scope_variables = self.get_function_call_args(func, func_call)

        # This is not necessary for native functions atm
        self.scope_stack.update_first(new_scope_variables)

        if isinstance(func, ast.NativeFunction):
            result = self.call_native_func(func, new_scope_variables)
        else:
            result = self.run(func.body)

        # Don't forget to destroy the created scope!
        self.scope_stack.pop()

        return result

    def get_function_call_args(self, func, func_call):
        """Returns a dict, containing {name: object} values. The names
        are the function's formal parameters, and the values are their runtime
        values

        :param ast.FuncCreation|ast.NativeFunction func:
        :param ast.FuncCall func_call:
        :return:
        """
        params = func.get_params_and_types()
        # flatten function arguments
        flat_arguments = []
        for expression in func_call.args.arg_list if func_call.args else []:
            if isinstance(expression.child, ast.FuncArguments):
                for child_expr in expression.child.arg_list:
                    flat_arguments.append(child_expr)
            else:
                flat_arguments.append(expression.child)
        # set in the new function scope the arguments as variables
        new_scope_variables = {}
        for (pname, ptype), arg_abstrat_value in zip(params, flat_arguments):
            arg_value = self.run(arg_abstrat_value)

            # TODO -> we don't check for types here, and we shouldn't
            #   What we should do is check types at parse time
            # scopes[0][pname] = [arg_value,
            # 'type-not-set-and-we-dont-need-to-set-it-yet']
            new_scope_variables[pname] = [
                arg_value, 'type-not-set-and-we-dont-need-to-set-it-yet']

        return new_scope_variables
