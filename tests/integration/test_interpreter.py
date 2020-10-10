from pygolang.interpreter import main
from tests.integration.io_callback_fixture import FakeIO


def test_prints_expressions_to_stdout():
    io = FakeIO([
        """func asdf( name1 int)name2{return 133}""",
        """asdf(3)""",
        """15""",
    ])
    state = {}

    try:
        import pydevd; pydevd.settrace('localhost', port=5678)
    except ImportError:
        print("\n\n\n")
        print(">>>VWH>>>: the pydevd module is not installed")
        print("\n\n\n\n\n")

    main(io, state)

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
