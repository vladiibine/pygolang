class PyLangRuntimeError(Exception):
    pass


class PyLangValueError(PyLangRuntimeError):
    pass


class StopPyGoLangInterpreterError(Exception):
    pass


class PyGoGrammarError(Exception):
    pass


class PyGoConsoleLogoffError(Exception):
    def __init__(self, *a, **kw):
        super(PyGoConsoleLogoffError, self).__init__(*a, **kw)
