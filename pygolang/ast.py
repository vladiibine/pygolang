class FuncCall:
    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args

    def get_signature(self):
        """
        :return: a list [(name, typename), ...] representing the params
            and their types
        """


class Func:
    def __init__(self, name, params, return_type, body):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body

    def get_params_and_types(self):
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
        # flatmap function params
        flat_param_definitions = []
        for nested_param in self.params.token:
            if nested_param.type == 'func_params':
                for single_param in nested_param.value.token:
                    flat_param_definitions.append(single_param)
            else:
                # it's a comma, not a nested param
                flat_param_definitions.append(nested_param)

        param_names = []
        param_types = []
        prev_token = None
        for token in flat_param_definitions:  # type: ply.lexer.LexToken
            if prev_token is None:
                param_names.append(token.value)
                prev_token = token
            elif token.type == 'NAME' and prev_token.type == 'NAME':
                param_types.extend(
                    [token.value] * (len(param_names) - len(param_types)))
                prev_token = token
            elif token.type == 'NAME' and prev_token.type == 'COMMA':
                param_names.append(token.value)
                prev_token = token
            else:
                prev_token = token  # handling commas
        params = list(zip(param_names, param_types))
        return params


class FuncParams:
    def __init__(self, token):
        self.token = token


class FuncReturnType:
    def __init__(self, token):
        self.token = token


class FuncBody:
    def __init__(self, statements):
        self.statements = statements


class FuncArguments:
    def __init__(self, arg_list):
        self.arg_list = arg_list


class Name:
    def __init__(self, value):
        self.value = value


class Expression:
    def __init__(self, children):
        """

        :param list[Node] children:
        """
        self.children = children


class Leaf:
    """Superclass for elements which are at the bottom of the ast tree.

    They represent their own value, and don't need further processing
    Examples: numbers, strings, arrays
    Examples of things NOT leafs: function bodies, assignments
    """
    value = None  # Leafs have values


class Number(Leaf):
    def __init__(self, value):
        self.value = value


class Operator:
    def __init__(self, operator, args_list):
        self.operator = operator
        self.args_list = args_list


class Assignment:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Statement:
    def __init__(self, value):
        self.value = value


class InterpreterStart:
    def __init__(self, value):
        self.value = value


class Root:
    def __init__(self, value):
        self.value = value


class Return:
    def __init__(self, value):
        self.value = value
