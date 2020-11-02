from pygolang.ast import ValueNotSet, TypedValue, AbstractRuntimeScope
from pygolang.errors import PyGoGrammarError


class ScopeStack:
    """
    TODO - very inefficient to pop/push at the start of an array
     Need to make the scopes management use dequeues.
     ALSO - we have 2 types of classes for scope management: one for types
     and one for run-time. Not sure we actually need those 2 categories of
     classes

    """
    def __init__(self, initial_state=None):
        self.scopes = initial_state or []

    def push(self, scope):
        self.scopes.insert(0, scope)

    def pop(self):
        return self.scopes.pop(0)

    def push_block_scope(self):
        self.push(BlockRuntimeScope({}))

    def declare_in_scopes(self, key, type_):
        """
        :param str key:
        :param ast.Type type_:
        :return:
        """
        # TODO - refactor declare-in-scopes, find-in-scopes and set-in-scopes
        #  These methods should be placed in the AbstractRuntimeScope class
        # Can only declare in the current scope
        usable_key = key

        self.scopes[0][usable_key] = [ValueNotSet, type_]

    def set_in_scopes(self, name, value):
        """
        :param str name:
        :param ast.TypedValue value:
        :return:
        """
        if not isinstance(value, TypedValue):
            raise PyGoGrammarError(f"Trying to set a typeless value: {value}")

        usable_scopes = list(self.scopes)
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

    @staticmethod
    def are_types_compatible(declared_type, assigned_value):
        if declared_type == assigned_value.type:
            return True

        return False

    def find_in_scopes(self, name):
        """
        :param str name:
        :return:
        """
        for scope in self.scopes:
            # Function scopes should be skipped when looking for variables
            # ..this might get more complicated when creating
            # if isinstance(scope, ast.FuncScope):
            #     continue
            if name in scope:
                return scope[name][0]

        # well... should raise an error if the name is not in any scope
        #  BUT it's really the job of the parser to prevent this situation

    def push_function_scope(self):
        self.scopes.insert(0, FuncRuntimeScope({}))

    def update_first(self, new_scope_variables):
        self.scopes[0].update(new_scope_variables)


class FuncRuntimeScope(AbstractRuntimeScope):
    pass


class PackageRuntimeScope(AbstractRuntimeScope):
    pass


class BlockRuntimeScope(AbstractRuntimeScope):
    pass