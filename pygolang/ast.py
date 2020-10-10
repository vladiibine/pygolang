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
