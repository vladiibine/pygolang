import io

from pygolang import ast


class _PrintlnClass(ast.NativeFunction):
    # TODO - function signature is totally wrong, because we don't have
    #  variadic, generic parameters like `...interface{}` (for the inputs)
    #  and `nil` for the outputs
    _params_and_types = [('a', ast.StringType), ]
    _rtype = [ast.IntType]

    type = ast.Type.create_func_type([p[1] for p in _params_and_types], _rtype)

    def call(self, side_effects, arguments):
        """ Mimics go's fmt.Println()

        :param pygolang.side_effects.SideEffects side_effects:
        :param dict[str,list[object,]] arguments:
        """
        f = io.StringIO()
        print(arguments['a'][0].to_pygo_repr(), end='', file=f)
        side_effects.to_stdout(f.getvalue())


Println = _PrintlnClass()
