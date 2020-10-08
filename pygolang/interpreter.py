import sys


class StopPyGoLangInterpreterError(Exception):
    pass


class IO:
    def __init__(self, stdout=None, stderr=None, stdin=None):
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr
        self.stdin = stdin or sys.stdin
        # ...add all file descriptors here
        # for all files, for all sockets, for everything that's IO

    def to_stdout(self, stuff):
        self.stdout.write(stuff)
        self.stdout.flush()

    def from_stdin(self):
        return self.stdin.readline().lstrip('\n')

    def interpreter_prompt(self):
        self.to_stdout("pygo> ")


def main(io=IO()):
    while True:
        try:
            io.interpreter_prompt()
            instruction_set = io.from_stdin()

            io.to_stdout("You wrote:\n{}".format(instruction_set))

        except StopPyGoLangInterpreterError:
            break


if __name__ == '__main__':
    main()
