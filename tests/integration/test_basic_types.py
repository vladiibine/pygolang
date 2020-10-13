from pygolang import ast
from pygolang.interpreter import main

from tests.integration.io_callback_fixture import FakeIO


def test_parse_bool_explicit():
    io = FakeIO(["var x bool = true"])

    scope = {}
    main(io)

    assert 'x' in scope
    assert scope['x'] is True
