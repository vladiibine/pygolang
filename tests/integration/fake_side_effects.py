from pygolang.side_effects import SideEffects
from pygolang.errors import StopPyGoLangInterpreterError


class FakeSideEffects(SideEffects):
    def __init__(self, stdin_as_str_list, fake_files=()):
        """
        :param list[str] stdin_as_str_list: list(or iterable) of strings, to
            simulate the lines from stdin
        :param list[dict] fake_files: Dict containing the 'path' and 'content'
            keys. Will be used instead of real files
        """
        self.stdin = stdin_as_str_list
        self.stdout = []
        self.stderr = []
        self.sleep_list = []  # for recording time.Sleep calls
        self.input_generator = None
        self.fake_files = fake_files

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

    def sleep(self, interval):
        self.sleep_list.append(interval)

    def interpreter_prompt(self):
        pass

    def newline(self):
        pass

    def format_stderr_for_debugging(self):
        return '\n'.join(str(e) for e in self.stderr)
