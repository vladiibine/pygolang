from pygolang import ast


class _SleepClass(ast.NativeFunction):
    # TODO - function signature is totally wrong, because we don't have
    #  variadic, generic parameters like `...interface{}` (for the inputs)
    #  and `nil` for the outputs
    _params_and_types = [('interval', ast.IntType), ]
    _rtype = [ast.IntType]

    type = ast.Type.create_func_type([p[1] for p in _params_and_types], _rtype)

    def call(self, side_effects, arguments):
        """ Mimics go's fmt.Println()

        :param pygolang.side_effects.SideEffects side_effects:
        :param dict[str,list[object,]] arguments:
        """
        side_effects.sleep(arguments['interval'][0].value)


Sleep = _SleepClass()
