###
# parsing section,
# these names are used via reflection, don't change them,
# and don't change their order
# from ply import yacc, lex
from pygolang.ast_runner import runner as pygo_runner
from pygolang import parser_setup
from pygolang.errors import PyLangRuntimeError, StopPyGoLangInterpreterError, \
    PyGoConsoleLogoffError
from pygolang.side_effects import SideEffects
from . import lexer_setup


def main(side_effects=SideEffects(), program_state=None):

    # Weird code, I know. The parser relies on reflection for finding
    # handler function names. It loads stuff from the global variables.
    # The module used for loading stuff I ASSUME is the one where the lexer
    # and parser are initialized.

    program_state = program_state if program_state is not None else {}

    # with lexer_setup.build_lexer(io) as lexer:
    # pygo_lexer = lexer_setup.PyGoLexer(io)
    lexer = lexer_setup.PyGoLexer(side_effects)
    parser = parser_setup.PyGoParser(side_effects, program_state)
    runner = pygo_runner.Runner(side_effects, program_state)

    while True:
        try:
            side_effects.interpreter_prompt()
            instruction_set = side_effects.from_stdin()

            code = parser.parse(instruction_set)
            runner.run(code)

            side_effects.newline()
            # io.to_stdout("You wrote:\n{}".format(instruction_set))

        except StopPyGoLangInterpreterError:
            break

        except PyLangRuntimeError as err:
            side_effects.to_stdout("Error: {}".format(err))

        except KeyboardInterrupt:
            try:
                side_effects.newline()
                side_effects.to_stdout("Do you really want to quit? [y/n] ")
                reply = side_effects.from_stdin()

                if (reply.strip() or '').lower() == 'y':
                    return
            except KeyboardInterrupt:
                return

        except PyGoConsoleLogoffError:
            return

        except Exception as err:
            import traceback as tb

            side_effects.to_stderr(
                "Unknown error occurred. Traceback for debugging:"
            )
            side_effects.to_stderr(tb.format_exc())
            side_effects.to_stderr(err)


if __name__ == '__main__':
    main()
