from pygolang import ast
from pygolang.interpreter import main
from tests.integration.io_callback_fixture import FakeIO


def test_prints_expressions_to_stdout():
    io = FakeIO([
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
    io = FakeIO([
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
    io = FakeIO([
        "var x int",
        "x=1",
        "x",
        "2",
        "func a(n int)int{return 3}",
        "a(0)",
    ])

    state = {}

    main(io, state)

    assert not io.stderr, '\n'.join(str(e) for e in io.stderr)
    assert io.stdout
    assert len(io.stdout) == 3
    assert io.stdout == ['1', '2', '3']


def test_operators_and_expressions():
    io = FakeIO([
        "func f()int{return 2}",
        "f() + 2"
    ])

    state = {}

    main(io, state)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['4']

