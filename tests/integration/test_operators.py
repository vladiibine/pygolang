from pygolang import ast
from pygolang.interpreter import main

from tests.integration.io_callback_fixture import FakeIO


def test_plus():
    io = FakeIO(['1+1'])

    state = {}

    main(io, state)

    assert io.stdout
    assert io.stdout == ['2']
    assert not io.stderr


def test_walrus_plus():
    io = FakeIO(['x := 1'])

    state = {}

    main(io, state)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert state['x'][0] == ast.Int(1)
    assert state['x'][1] == ast.IntType
