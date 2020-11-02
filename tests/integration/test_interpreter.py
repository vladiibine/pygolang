from pygolang import ast
from pygolang.repl import main
from tests.fake_side_effects import FakeSideEffects


def test_prints_expressions_to_stdout():
    io = FakeSideEffects([
        """func asdf( name1 int)int{return 133}""",
        """asdf(3)""",
        """15""",
    ])
    state = {}

    main(io, state)

    assert io.stdout
    assert len(io.stdout) == 2
    assert io.stdout == ['133', '15']


def test_assignment_from_variable():
    io = FakeSideEffects([
        """var x int = 1""",
        """var y int = x""",
        """y"""
    ])
    state = {}

    main(io, state)

    assert io.stdout
    assert len(io.stdout) == 1
    assert io.stdout == ['1']

    assert 'y' in state
    assert state['y'][0] == ast.Int(1)
    assert state['y'][1] == ast.IntType


def test_interpreter_prints_out_things():
    io = FakeSideEffects([
        "var x int",
        "x=1",
        "x",
        "2",
        "func a(n int)int{return 3}",
        "a(0)",
        "v := true",
        "v"
    ])

    state = {}

    main(io, state)

    assert not io.stderr, '\n'.join(str(e) for e in io.stderr)
    assert io.stdout
    assert len(io.stdout) == 4
    assert io.stdout == ['1', '2', '3', 'true']


def test_operators_and_expressions():
    io = FakeSideEffects([
        "func f()int{return 2}",
        "f() + 2"
    ])

    state = {}

    main(io, state)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['4']


def test_parses_multiple_operations_in_one_gulp():
    side_effects = FakeSideEffects([
        """
        var x int = 2
        x = 4
        import "fmt"
        fmt.Println(x)
        """
    ])
    scope = {}
    main(side_effects, scope)

    assert not side_effects.stderr, side_effects.format_stderr_for_debugging()
    assert side_effects.stdout == ['4']


def test_raises_error_on_missing_semicolon():
    side_effects = FakeSideEffects([
        "3 4"
    ])

    main(side_effects)

    assert side_effects.stderr
    assert len(side_effects.stderr) == 4, side_effects.format_stderr_for_debugging()
    assert side_effects.stderr[0] == 'pygo: Syntax error at \'4\''


def test_semicolons_work_as_statement_terminators():
    side_effects = FakeSideEffects([
        '3; 4;'
    ])

    main(side_effects)

    assert not side_effects.stderr, side_effects.format_stderr_for_debugging()
    assert side_effects.stdout == ['3', '4']
