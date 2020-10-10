import sys

###
# parsing section,
# these names are used via reflection, don't change them,
# and don't change their order
# from ply import yacc, lex

from pygolang import parser_setup, ast_runner
from . import lexer_setup


class PyLangRuntimeError(Exception):
    pass


class PyLangValueError(PyLangRuntimeError):
    pass


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
        self.stdout.write(str(stuff))
        self.stdout.flush()

    def to_stderr(self, stuff):
        self.stderr.write(str(stuff))
        self.stderr.flush()

    def from_stdin(self):
        return self.stdin.readline().lstrip('\n')

    def interpreter_prompt(self):
        self.to_stdout("pygo> ")

    def newline(self):
        self.to_stdout('\n')


def main(io=IO(), program_state=None):

    # Weird code, I know. The parser relies on reflection for finding
    # handler function names. It loads stuff from the global variables.
    # The module used for loading stuff I ASSUME is the one where the lexer
    # and parser are initialized.

    program_state = program_state if program_state is not None else {}

    with lexer_setup.build_lexer(io) as lexer:
        parser = parser_setup.PyGoParser(io, program_state)
        runner = ast_runner.Runner(io, program_state)

        while True:
            try:
                io.interpreter_prompt()
                instruction_set = io.from_stdin()

                code = parser.parse(instruction_set)
                runner.run(code)

                io.newline()
                # io.to_stdout("You wrote:\n{}".format(instruction_set))

            except StopPyGoLangInterpreterError:
                break

            except PyLangRuntimeError as err:
                io.to_stdout("Error: {}".format(err))


if __name__ == '__main__':
    main()
