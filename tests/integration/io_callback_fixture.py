from pygolang.io_callback import IO
from pygolang.errors import StopPyGoLangInterpreterError


class FakeIO(IO):
    def __init__(self, stdin_as_str_list):
        """
        :param list[str] stdin_as_str_list: list(or iterable) of strings, to
            simulate the lines from stdin
        """
        self.stdin = stdin_as_str_list
        self.stdout = []
        self.stderr = []
        self.input_generator = None
        # super().__init__()

    def from_stdin(self):
        def iterate_over_stdin():
            for line in self.stdin:
                yield line

            raise StopPyGoLangInterpreterError

        if not self.input_generator:
            self.input_generator = iterate_over_stdin()

        return next(self.input_generator)

    def to_stdout(self, stuff):
        self.stdout.append(stuff)

    def to_stderr(self, stuff):
        self.stderr.append(stuff)

    def interpreter_prompt(self):
        pass

    def newline(self):
        pass

    def format_stderr_for_debugging(self):
        return '\n'.join(str(e) for e in self.stderr)
