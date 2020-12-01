###
# parsing section,
# these names are used via reflection, don't change them,
# and don't change their order
# from ply import yacc, lex
from pygolang.runtime import interpreter as pygo_interpreter
from pygolang import parser_setup
from pygolang.runtime.importer import Importer
from pygolang.errors import PyLangRuntimeError, StopPyGoLangInterpreterError, \
    PyGoConsoleLogoffError
from pygolang.runtime.namespaces import FileRuntimeNamespace, GlobalNamespace, \
    PackageNamespace
from pygolang.side_effects import SideEffects
from . import lexer_setup


def main(
        side_effects=SideEffects(),
        program_state_factory=lambda: GlobalNamespace({'main': PackageNamespace({})}),
        importer=None):

    # Weird code, I know. The parser relies on reflection for finding
    # handler function names. It loads stuff from the global variables.
    # The module used for loading stuff I ASSUME is the one where the lexer
    # and parser are initialized.

    # program_state = program_state if program_state is not None else {}

    importer = importer or Importer(side_effects)

    lexer = lexer_setup.PyGoLexer(side_effects)
    parser = parser_setup.PyGoParser(side_effects, importer, lexer=lexer.lexer)

    # program_namespace = FileRuntimeNamespace(program_state)
    interpreter = pygo_interpreter.Interpreter(side_effects, program_state_factory())

    while True:
        try:
            side_effects.interpreter_prompt()
            instruction_set = side_effects.from_stdin()

            code = parser.parse(instruction_set)
            interpreter.run(code)

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
