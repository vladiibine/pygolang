import importlib

from pygolang import ast
from pygolang.ast_runner.importer import Importer
from pygolang.errors import PyGoGrammarError


class Runner:
    def __init__(self, side_effects, state, importer=None):
        """

        :param side_effects:
        :param dict|ast.AbstractRuntimeScope state: the program's starting
        state
        """
        self.side_effects = side_effects
        self.importer = importer or Importer(side_effects)
        # TODO -> access to this needs to be replaced with a call to a
        #  method which searches for variables in a list of scopes
        #  AND if it writes something, it writes in the first scope it gets
        if isinstance(state, dict):
            self.state = ast.PackageRuntimeScope(state)

        elif isinstance(state, ast.AbstractRuntimeScope):
            self.state = state
        else:
            raise Exception(
                "The program's state should be a module scope or a dict")

    def run(self, code, scopes=None):
        value = None
        scopes = scopes or [self.state]

        if isinstance(code, ast.Root):
            value = self.run(code.value, scopes)  # Root

        elif isinstance(code, ast.InterpreterStart):
            for stmt in code.statements:
                value = self.run(stmt, scopes)

            # value = self.run(code.statements, scopes)  # InterpreterStart
            if value is not None:
                self.side_effects.to_stdout(value.to_pygo_repr())

        elif isinstance(code, ast.Import):
            # 0. TODO -> Determine the import path. Will be useful for when
            #     importing other packages, and for displaying errors like
            #     go does. Go displays all the paths where it looked for
            #     packages, looking at env vars like $GOPATH and $GOROOT
            # 1. find the imported module
            # 2. import it
            # 3. get a list of (key, value) pairs
            # 4. add the keys/values to the current namespace

            # Try to import from the builtin modules
            new_variables = []
            new_variables.extend(
                self.importer.import_from_stdlib(code.import_str))
            if new_variables:
                for qualified_name, obj_type, obj in new_variables:
                    self.declare_in_scopes(qualified_name, obj_type, scopes)
                    self.set_in_scopes(qualified_name, obj, scopes)
                return

            found_files = False
            for source in self.importer.import_from_gopath(code.import_str):
                found_files = True
                pass

            if found_files:
                return

            # new_variables.extend(
            #     self.importer.import_from_modules(code.import_str))
            # if new_variables:
            #     # yes, the code below is duplicated. Is it really worth
            #     # creating a method? don't think so
            #     for qualified_name, obj_type, obj in new_variables:
            #         self.declare_in_scopes(qualified_name, obj_type, scopes)
            #         self.set_in_scopes(qualified_name, obj, scopes)
            #     return

            self.side_effects.to_stderr(
                f'cannot find package "{code.import_str}" in any of'
            )

        elif isinstance(code, ast.Block):
            for stmt in code.statements:
                scopes.insert(0, ast.BlockRuntimeScope({}))
                self.run(stmt, scopes)  # Block
                scopes.pop(0)

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
                value = self.run(stmt, scopes)  # FuncBody
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
            self.declare_in_scopes(key, type_, scopes)
            if code.value is not ast.ValueNotSet:
                assigned_value = self.run(code.value)  #
                try:
                    self.set_in_scopes(key, assigned_value, scopes)
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
            assigned_value = self.run(code.value, scopes)  # Assignment
            self.set_in_scopes(key[0], assigned_value, scopes)
            #
            #     # Global scope, until we implement per-something-else scope
            #     self.set_in_scopes(key, assigned_value, scopes)
            # else:
            #     raise PyGoGrammarError(f"Can't assign value to {key}!")

        elif isinstance(code, ast.FuncCreation):
            self.declare_in_scopes(
                key=code.name,
                type_=ast.FuncCreation.get_func_type(code.params, code.return_type),
                scopes=scopes
            )
            self.set_in_scopes(code.name, code, scopes)

        # return result

        elif isinstance(code, ast.Name):
            # TODO - replace global state with scopes
            # return self.state[exp.value]
            value = self.find_in_scopes(code.get_qualified_name(), scopes)

        elif isinstance(code, ast.Operator):
            value = self.run_operator(code, scopes)

        elif isinstance(code, ast.Value):
            value = code

        elif isinstance(code, ast.Expression):
            value = self.run(code.child, scopes)  # Expression

        elif isinstance(code, ast.Return):
            value = self.run(code.value, scopes)  # Return

        elif isinstance(code, ast.FuncCall):
            value = self.call_func(code, scopes)  # FuncCall

        elif isinstance(code, ast.Statement):
            value = self.run(code.value, scopes)  # Statement

        return value

    # TODO - move this to another class
    @staticmethod
    def import_from_stdlib(import_stmt):
        """Import names from the standard library
        (functionality re-implemented in python)

        :param pygolang.ast.Import import_stmt:
        """
        new_variables = []
        try:
            module = importlib.import_module(
                f'.stdlib.{import_stmt.import_str}', 'pygolang'
            )

            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, ast.NativeFunction):
                    qualified_name = '.'.join([import_stmt.import_str, name])
                    new_variables.append((qualified_name, obj.type, obj))
        except ImportError:
            pass

        return new_variables

    def set_in_scopes(self, name, value, scopes):
        """

        :param str name:
        :param ast.TypedValue value:
        :param list[ast.AbstractRuntimeScope] scopes:
        :return:
        """
        if not isinstance(value, ast.TypedValue):
            raise PyGoGrammarError(f"Trying to set a typeless value: {value}")

        usable_scopes = list(scopes)
        while usable_scopes:
            current_scope = usable_scopes.pop(0)
            if name in current_scope:
                _, type_ = current_scope[name]

                # TODO -> should not do these kinds of checks at run-time
                #   assignments and declarations have already been checked
                #   at parse-time....Well, maybe if we have dynamic types,
                #   created at run-time, this is justified, but this has not
                #   been the case so far
                if self.are_types_compatible(
                        declared_type=type_, assigned_value=value):
                    current_scope[name][0] = value
                    return
                else:
                    raise PyGoGrammarError(
                        f"Runtime error. Trying to set value {value} "
                        f"for declared type {type_}. This code should not "
                        f"have been executed at all, as it's syntactically "
                        f"wrong"
                    )

    def are_types_compatible(self, declared_type, assigned_value):
        if declared_type == assigned_value.type:
            return True

        return False

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
                return scope[name][0]

        # well... should raise an error if the name is not in any scope
        #  BUT it's really the job of the parser to prevent this situation

    def run_operator(self, operator_expr, scopes):
        """
        :param ast.Operator operator_expr:
        :param list[dict] scopes:
        :return:
        """
        operands = [
            self.run(operand_exp, scopes)
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

    def call_func(self, func_call, scopes):
        # 1. find the function's parameters
        # 2. match them against the arguments
        # 3. set the parameters as variables in the newly created scope
        # 4. run the function's body using the new and previous scopes
        # 5. profit!
        scopes = scopes or []
        # This is not necessary for native functions atm. They're just called
        # with their arguments, they don't need the scopes, as they don't
        # interact with normal variables
        scopes.insert(0, ast.FuncRuntimeScope({}))

        func = self.find_in_scopes(func_call.func_name.get_qualified_name(), scopes)  # type: ast.Func

        new_scope_variables = self.get_function_call_args(
            func, func_call, scopes)

        # This is not necessary for native functions atm
        scopes[0].update(new_scope_variables)

        if isinstance(func, ast.NativeFunction):
            result = self.call_native_func(func, new_scope_variables)
        else:
            result = self.run(func.body, scopes=scopes)

        # Don't forget to destroy the created scope!
        scopes.pop(0)

        return result

    def get_function_call_args(self, func, func_call, scopes):
        """Returns a dict, containing {name: object} values. The names
        are the function's formal parameters, and the values are their runtime
        values

        :param ast.FuncCreation|ast.NativeFunction func:
        :param ast.FuncCall func_call:
        :param list[ast.AbstractRuntimeScope] scopes:
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
            arg_value = self.run(arg_abstrat_value, scopes)

            # TODO -> we don't check for types here, and we shouldn't
            #   What we should do is check types at parse time
            # scopes[0][pname] = [arg_value,
            # 'type-not-set-and-we-dont-need-to-set-it-yet']
            new_scope_variables[pname] = [
                arg_value, 'type-not-set-and-we-dont-need-to-set-it-yet']

        return new_scope_variables

    def declare_in_scopes(self, key, type_, scopes):
        """
        :param str key:
        :param ast.Type type_:
        :param list[ast.AbstractRuntimeScope] scopes:
        :return:
        """
        # TODO - refactor declare-in-scopes, find-in-scopes and set-in-scopes
        #  These methods should be placed in the AbstractRuntimeScope class
        # Can only declare in the current scope
        usable_key = key

        scopes[0][usable_key] = [ast.ValueNotSet, type_]