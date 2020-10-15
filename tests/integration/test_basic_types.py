from pygolang import ast
from pygolang.interpreter import main

from tests.integration.io_callback_fixture import FakeIO


def test_parse_bool_literal():
    io = FakeIO(["true", 'false'])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['true', 'false']


def test_parse_bool_explicit():
    io = FakeIO(["var x bool = true"])

    scope = {}
    main(io, scope)

    assert not io.stderr
    assert not io.stdout
    assert 'x' in scope
    assert scope['x'][0] == ast.BoolLiteralTrue()
