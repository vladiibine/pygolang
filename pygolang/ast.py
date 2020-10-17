import operator
from collections import defaultdict

from pygolang import common_grammar
from pygolang.errors import PyGoGrammarError


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
    def __init__(self, func_name, args, type):
        self.func_name = func_name
        self.args = args
        self.type = type

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
        super(FuncCreation, self).__init__(
            self,
            self.get_func_type(params, return_type)
        )

    def get_params_and_types(self):
        return self.get_params_and_types_static(self.params.params)

    @staticmethod
    def get_params_and_types_static(params):
        """

        :param list[YaccSymbol|LexToken] params:
        :return:
        """
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
        for nested_param in params:
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

    @classmethod
    def get_func_type(cls, params, rtype):
        """Creates a type, which is the function type.

        Contains information about the parameters types and type returned

        :param FuncParams params:
        :param FuncReturnType rtype:
        :return:
        """
        param_types = [e[1] for e in cls.get_params_and_types_static(params.params)]
        flat_return_type = []
        for type_decl in rtype:
            flat_return_type.append(type_decl.value)

        # Create a signature for this function type, based on the types of its
        # input params, and its returned type
        return Type(
            f"func ({', '.join(str(e) for e in param_types)}) {', '.join(str(e) for e in flat_return_type)}",
            rtype=flat_return_type[0] if len(flat_return_type) == 1 else flat_return_type or None
        )

    def get_return_type(self, func):
        """
        :param FuncCreation func:
        :return:
        """
        return self.return_type.rtype


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

    def __repr__(self):
        return f"<Name: '{self.value}'>"


class Expression:
    def __init__(self, child, type_scope):
        """

        :param TypeScope type_scope:
        :param child:
        """
        self.child = child
        self.type_scope_stack = type_scope
        self.type = self.determine_type(child, type_scope)

    def determine_type(self, child, type_scope):
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
        if isinstance(child, Name):
            return type_scope.get_variable_type(child.value)

        elif isinstance(child, TypedValue):
            return child.type

        elif isinstance(child, Operator):
            return child.type

        # TODO - remove this hack!
        #  It's a hack because the func_arg_list non-final grammar element
        #  instead of returning a list of expressions, returns a list of
        #  expressions which contain FunctionArguments yet again
        #  We should make the p_func_arguments handler flatten all expressions
        #  into the FunctionArgument's .arg_list
        elif isinstance(child, FuncArguments):
            return child.arg_list[0].type

    def __repr__(self):
        return f"<Expression: {self.child} of type {self.type}>"


class OperatorDelegatorMixin:
    """Used for performing operations using its .value attribute
    """
    def __add__(self, other):
        return self.__class__(self.value + other.value)

    def __sub__(self, other):
        return self.__class__(self.value - other.value)

    def __mul__(self, other):
        return self.__class__(self.value * other.value)

    # def __divmod__(self, other):
    #     return self.__class__(self.value % other.value)

    def __floordiv__(self, other):
        return self.__class__(self.value // other.value)

    def __mod__(self, other):
        return self.__class__(self.value % other.value)

    def __gt__(self, other):
        return BoolValue(self.value > other.value)

    def __lt__(self, other):
        return BoolValue(self.value < other.value)

    def __ge__(self, other):
        return BoolValue(self.value >= other.value)

    def __le__(self, other):
        return BoolValue(self.value <= other.value)

    def __ne__(self, other):
        return BoolValue(self.value != other.value)

    def __eq__(self, other):
        return BoolValue(self.value == other.value)

    def __and__(self, other):
        return BoolValue(self.value and other.value)

    def __or__(self, other):
        return BoolValue(self.value or other.value)

    @staticmethod
    def not_(first, second):
        return BoolValue(first.value, second.value)


class Int(TypedValue, Value, OperatorDelegatorMixin):
    def __init__(self, value):
        self.value = value
        super(Int, self).__init__(value, IntType)

    def __repr__(self):
        return f"ast.Int({self.value})"

    def to_pygo_repr(self):
        return f"{self.value}"


class Operator:
    def __init__(self, operator_symbol, operator_token, args_list):
        """
        :param str operator_symbol: the characters of the operator, eg: '+'
        :param operator_token: The name of the operator, as defined in the
            grammar. Names are members of `pygolang.common_grammar.OPERATORS`
        :param args_list:
        """
        self.operator = operator_symbol
        self.args_list = args_list
        self.type, self.operator_pyfunc = self.determine_type_and_py_operator(
            operator_symbol, operator_token, args_list
        )

        # TODO - operators will have a parse-time type.
        #  This will be used for type checking
        #  This type will be determined based on the operator, and the types
        #  of the arguments

    def determine_type_and_py_operator(self, symbol, operator_token, arg_list):
        try:
            type_, py_operator = OPERATOR_TYPE_MAP[
                operator_token][arg_list[0].type][arg_list[1].type]

            if {type_, py_operator} == {None}:
                raise PyGoGrammarError(
                    f"Operation not defined ({symbol}) "
                    f"for {', '.join(str(e) for e in arg_list)} "
                    f"of types {', '.join(str(e.type) for e in arg_list)}"
                )

            return type_, py_operator

        except AttributeError:
            raise PyGoGrammarError(
                f"Invalid operation. No `type` attribute present for one of "
                f"the operands: {arg_list[0]} {arg_list[1]}"
            )


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


# TODO
#  Not sure I need all these 4 types of scopes :| One is probably enough
class FuncRuntimeScope(AbstractRuntimeScope):
    pass


class ModuleRuntimeScope(AbstractRuntimeScope):
    pass


class BlockRuntimeScope(AbstractRuntimeScope):
    pass


class BoolValue(TypedValue, OperatorDelegatorMixin):
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

    def __repr__(self):
        return f"<BoolValue: {self.value}>"

    def to_pygo_repr(self):
        return f"{str(self.value).lower()}"


class Type:
    def __init__(self, repr, rtype=None):
        self.repr = repr
        self.rtype = rtype

    def __str__(self):
        return f"{self.repr}"

    __repr__ = __str__

    def is_assignable_from(self, other):
        if self == other:
            return True

        return False

    def __eq__(self, other):
        return self.repr == other.repr

    def __hash__(self):
        return hash(self.repr)


BoolType = Type("BoolType")
FuncType = Type("FuncType")
IntType = Type("IntType")
StringType = Type("StringType")

# SINGLETONS
BoolLiteralFalse = BoolValue(False)
BoolLiteralTrue = BoolValue(True)

# Singleton to mark that a variable was only declared, but not initialized
ValueNotSet = ReprHelper('NotSet')

# Map of resulting types after applying an operator, and actual python operator
# to apply
# Example: For '+' applied to IntType and IntType, the python operator to apply
#  is operator.add, and the resulting type will be IntType
_OPERATOR_TYPE_TABLE = [
    ###
    # Operators on Int
    # Arithmetic operators
    [common_grammar.OPERATORS.PLUS, IntType, IntType, IntType, operator.add],
    [common_grammar.OPERATORS.DIVIDE, IntType, IntType, IntType, operator.floordiv],
    [common_grammar.OPERATORS.TIMES, IntType, IntType, IntType, operator.mul],
    [common_grammar.OPERATORS.MINUS, IntType, IntType, IntType, operator.sub],
    [common_grammar.OPERATORS.MODULO, IntType, IntType, IntType, operator.mod],

    # boolean operators (still on Int)
    [common_grammar.OPERATORS.BOOLEQUALS, IntType, IntType, BoolType, operator.eq],
    [common_grammar.OPERATORS.BOOLNOTEQUALS, IntType, IntType, BoolType, operator.ne],
    [common_grammar.OPERATORS.GREATER, IntType, IntType, BoolType, operator.gt],
    [common_grammar.OPERATORS.GREATEREQ, IntType, IntType, BoolType, operator.ge],
    [common_grammar.OPERATORS.LESSER, IntType, IntType, BoolType, operator.lt],
    [common_grammar.OPERATORS.LESSEREQ, IntType, IntType, BoolType, operator.le],

    # operators on BOOL
    [common_grammar.OPERATORS.BOOLEQUALS, BoolType, BoolType, BoolType, operator.eq],
    [common_grammar.OPERATORS.BOOLNOTEQUALS, BoolType, BoolType, BoolType, operator.ne],
    [common_grammar.OPERATORS.BOOLAND, BoolType, BoolType, BoolType, operator.and_],
    [common_grammar.OPERATORS.BOOLOR, BoolType, BoolType, BoolType, operator.or_],
    [common_grammar.OPERATORS.NOT, BoolType, BoolType, BoolType, OperatorDelegatorMixin.not_],
]


def initialize_operator_type_map():
    result = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [None, None])))
    for op, arg1_type, arg2_type, return_type, py_operator in _OPERATOR_TYPE_TABLE:
        result[op.value][arg1_type][arg2_type] = [return_type, py_operator]

    return result


# {operator_token: {type1: {type2: [resulting_type, python_operator]}}}
OPERATOR_TYPE_MAP = initialize_operator_type_map()


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
        """
        :return:
        :rtype: TypeScope
        """
        return self.scopes[-1]


class Conditional:
    def __init__(self, expression_block_pairs, final_block, scope):
        """

        :param list expression_block_pairs:
            list of pairs(expression, block)
        :param final_block: a list of statements, to execute as the fallback
            for the chain of if-else-if-else.....if-else statements
        :param TypeScope scope:
        """
        self.expression_block_pairs = expression_block_pairs
        self.final_block = final_block
        self.scope = scope


class Block:
    def __init__(self, statements):
        """

        :param list statements: a list of statements
        """
        self.statements = statements
