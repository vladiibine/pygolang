###
# parsing section,
# these names are used via reflection, don't change them,
# and don't change their order
# from ply import yacc, lex

from pygolang import parser_setup, ast_runner
from pygolang.errors import PyLangRuntimeError, StopPyGoLangInterpreterError, \
    PyGoConsoleLogoffError
from pygolang.io_callback import IO
from . import lexer_setup


def main(io=IO(), program_state=None):

    # Weird code, I know. The parser relies on reflection for finding
    # handler function names. It loads stuff from the global variables.
    # The module used for loading stuff I ASSUME is the one where the lexer
    # and parser are initialized.

    program_state = program_state if program_state is not None else {}

    # with lexer_setup.build_lexer(io) as lexer:
    # pygo_lexer = lexer_setup.PyGoLexer(io)
    lexer = lexer_setup.PyGoLexer(io)
    parser = parser_setup.PyGoParser(io, program_state)
    runner = ast_runner.Runner(io, program_state)

    # try:
    #     import pydevd; pydevd.settrace('localhost', port=5678)
    # except ImportError:
    #     print("\n\n\n")
    #     print(">>>VWH>>>: the pydevd module is not installed")
    #     print("\n\n\n\n\n")

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

        except KeyboardInterrupt:
            try:
                io.newline()
                io.to_stdout("Do you really want to quit? [y/n] ")
                reply = io.from_stdin()

                if (reply.strip() or '').lower() == 'y':
                    return
            except KeyboardInterrupt:
                return

        except PyGoConsoleLogoffError:
            return

        except Exception as err:
            import traceback as tb

            io.to_stderr(
                "Unknown error occurred. Traceback for debugging:"
            )
            io.to_stderr(tb.format_exc())
            io.to_stderr(err)


if __name__ == '__main__':
    main()
