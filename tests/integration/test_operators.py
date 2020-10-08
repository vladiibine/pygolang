from pygolang.interpreter import main, StopPyGoLangInterpreterError, IO


class FakeIO(IO):
    def __init__(self, in_):
        """
        :param list[str] in_:
        """
        self.in_ = in_
        self.out = []
        self.input_generator = None
        super().__init__()

    def from_stdin(self):
        def iterate_over_stdin():
            for line in self.in_:
                yield line

            raise StopPyGoLangInterpreterError

        if not self.input_generator:
            self.input_generator = iterate_over_stdin()

        return next(self.input_generator)

    def to_stdout(self, stuff):
        self.out.append(stuff)

    def interpreter_prompt(self):
        pass

    newline = interpreter_prompt


def test_plus():
    io = FakeIO(['1+1'])

    main(io)

    assert len(io.out) == 1

    assert io.out[0] == 2
