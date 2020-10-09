from pygolang.interpreter import main
from tests.integration.io_callback_fixture import FakeIO


def test_function_call():
    io = FakeIO([
        """func asdf( name1 int)name2{return 133}""",
        """asdf(3)""",
        """15""",
    ])
    state = {}

    main(io, state)

    # assert 'x' in state
    # assert state['x'] == 133

    assert io.stdout
    assert len(io.stdout) == 2
    assert io.stdout == [133, 15]


def test_assignment_from_variable():
    io = FakeIO([
        """x=1""",
        """y=x""",
        """y"""
    ])
    state = {}

    main(io, state)

    assert io.stdout
    assert len(io.stdout) == 1
    assert io.stdout == [1]

    assert 'y' in state
    assert state['y'] == 1
