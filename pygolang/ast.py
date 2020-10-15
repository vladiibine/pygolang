class Value:
    """Superclass for elements which are at the bottom of the ast tree.

    They represent their own value, and don't need further processing
    Examples: numbers, strings, arrays
    Examples of things NOT leafs: function bodies, assignments
    """
    value = None  # Leafs have values


class TypedValue(Value):
    def __init__(self, value, type):
        """
        :param object value:
        :param Type type:
        """
        self.value = value
        self.type = type


class ReprHelper:
    def __init__(self, repr_string):
        self.repr_string = repr_string

    def __str__(self):
        return self.repr_string

    __repr__ = __str__


class FuncCall:
    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args

    def get_signature(self):
        """
        :return: a list [(name, typename), ...] representing the params
            and their types
        """


class FuncCreation(TypedValue):
    def __init__(self, name, params, return_type, body):
        """
        :param str name:
        :param FuncParams params:
        :param FuncReturnType return_type:
        :param FuncBody body:
        """
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
        super(FuncCreation, self).__init__(self, FuncType)

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
        for nested_param in self.params.params:
            if nested_param.type == 'func_params':
                for single_param in nested_param.value.params:
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
            elif token.type == 'type_declaration' and prev_token.type == 'NAME':
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
    def __init__(self, params):
        self.params = params


class FuncReturnType:
    def __init__(self, rtype):
        self.rtype = rtype


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
    def __init__(self, child, type_scope):
        """

        :param TypeScope type_scope:
        :param child:
        """
        self.child = child
        self.type_scope_stack = type_scope
        self.type = self.determine_type()

    def determine_type(self):
        """
        :return:
        """
        # TODO -> figure out how we build these parse-time scopes
        #  because they're not the same as the run-time ones.
        #  At run-time, a function can get called multiple times, and scopes
        #  will be created and destroyed BUT, the parse-time scopes will be
        #  static. The names/types in them will not change.

        """
        SO, determining the type of an expression can't be done in just 1 step
        because golang has funny-scopes. Names of functions are evaluated
        lazily, but names of variables are evaluated eagerly.
        This allows definitions of functions to appear after they're called
        but doesn't allow usage of variables before they're declared, not even
        from anonymous functions.
            
        """
        pass


class OperatorDelegatorMixin:
    """Used for performing operations using its .value attribute
    """
    def __add__(self, other):
        return self.__class__(self.value + other.value)

    def __sub__(self, other):
        return self.__class__(self.value - other.value)

    def __mul__(self, other):
        return self.__class__(self.value * other.value)

    def __divmod__(self, other):
        return self.__class__(self.value.__divmod__(other.value))


class Int(TypedValue, Value, OperatorDelegatorMixin):
    def __init__(self, value):
        self.value = value
        super(Int, self).__init__(value, IntType)

    def __eq__(self, other):
        if isinstance(other, Int):
            return self.value == other.value

    def __repr__(self):
        return f"ast.Int({self.value})"

    def to_pygo_repr(self):
        return f"{self.value}"


class Operator:
    def __init__(self, operator, args_list):
        self.operator = operator
        self.args_list = args_list


class Assignment:
    def __init__(self, name, value, type_scope):
        """

        :param str name:
        :param TypedValue value:
        :param TypeScope type_scope:
        """
        self.name = name
        self.value = value
        self.type_scope = type_scope

        self.validate_types()

        # raise NotImplementedError(
        #     "TODO implement a type check OR mark as solvable later"
        # )

    def validate_types(self):
        target_type = self.type_scope.get_variable_type(self.name)
        type_to_assign = self.value.type

        if not target_type.is_assignable_from(type_to_assign):
            raise Exception(
                f"Can't assign type ({type_to_assign}) to variable "
                f"({self.name}) of type ({target_type})"
            )
        # if self.value.type.is_assignable_from()
        # pass


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


class AbstractRuntimeScope:
    def __init__(self, scope_dict):
        self._scope_dict = scope_dict

    def __getitem__(self, item):
        return self._scope_dict[item]

    def __setitem__(self, key, value):
        self._scope_dict[key] = value

    def __delitem__(self, key):
        del self._scope_dict[key]

    def __contains__(self, item):
        return item in self._scope_dict

    def __repr__(self):
        return f"{self.__class__.__name__}({self._scope_dict})"


class FuncRuntimeScope(AbstractRuntimeScope):
    pass


class ModuleRuntimeScope(AbstractRuntimeScope):
    pass


class BoolValue(TypedValue):
    _instance_cache = {}

    def __new__(cls, value):
        if value not in cls._instance_cache:
            new_obj = object.__new__(cls)
            cls.__init__(new_obj, value)
            cls._instance_cache[value] = new_obj

        return cls._instance_cache[value]

    def __init__(self, value):
        super(BoolValue, self).__init__(value=value, type=BoolType)

    def __eq__(self, other):
        if isinstance(other, BoolValue):
            return self.value == other.value

    def to_pygo_repr(self):
        return f"{str(self.value).lower()}"


class Type:
    def __init__(self, repr):
        self.repr = repr

    def __str__(self):
        return f"{self.repr}"

    __repr__ = __str__

    def is_assignable_from(self, other):
        if self == other:
            return True

        return False

    def __eq__(self, other):
        return self.repr == other.repr


BoolType = Type("BoolType")
FuncType = Type("FuncType")
IntType = Type("IntType")
StringType = Type("StringType")

# SINGLETONS
BoolLiteralFalse = BoolValue(False)
BoolLiteralTrue = BoolValue(True)

# Singleton to mark that a variable was only declared, but not initialized
ValueNotSet = ReprHelper('NotSet')


class Declaration:
    def __init__(self, name, type, type_scope, value=ValueNotSet):
        """
        :param name:
        :param type:
        :param value:
        :param TypeScope type_scope:
        """
        self.name = name
        self.type = type
        self.value = value
        self.type_scope = type_scope

        self.type_scope.declare_variable_type(name, type)


class TypeScope:
    """Keeps track of variable types within a lexical scope"""

    def __init__(self, parent):
        """
        :param TypeScope|None parent: ...or None for the root scope
        """
        self.parent = parent

        # {<name> : <type>}
        self.scope = {}

    def declare_variable_type(self, name, type):
        self.scope[name] = type

    def get_variable_type(self, name):
        tscope = self

        # beware of cycles!
        while tscope:
            if name in tscope.scope:
                return tscope.scope[name]
            tscope = tscope.parent


class TypeScopeStack:
    """Used at parse-time, to determine operations have compatible types

    For instance
    x = 123 // is this allowed? is x declared as some number type?

    ...or
    asdf() == zxcv() ...is this allowed? Are the 2 returned types comparable?

    How would we go about solving this problem?
    1. Each time a program starts, a TypeScope is created
    2. Each time a new function is created, a new TypeScope is created
    2.1. Impl detail -> we can create scopes when the "func" keyword is parsed
        for functions or when the "{" symbol is parsed, for blocks
    2.2. We can close scopes when the function/block is created in the
        p_* methods
    3. Each time a new block is created (excluding function bodies), a nea TS
        is created
    4. All TSs have exactly 1 parent, leading all the way up to the program's
        TS
    5. All type declarations will mark their types in the corresponding TS
    6. Function calls -> functions can be defined after a TS is created,
        and type checking for them can be left until after all parsing has
        completed
    7. Lookups: Assignments -> where do they get a scope, to search/define
        stuff in? ...well, there's always 1 scope on the stack to set things
        in. And it has parents, so there's always going to be a scope to search
        stuff in.

    """
    def __init__(self):
        self.scopes = [TypeScope(parent=None)]

    def create_scope(self):
        previous_scope = self.scopes[-1]
        self.scopes.append(TypeScope(parent=previous_scope))

    def pop_scope(self):
        self.scopes.pop()

    def get_current_scope(self):
        return self.scopes[-1]
