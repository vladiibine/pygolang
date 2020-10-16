from pygolang import ast
from pygolang.interpreter import main

from tests.integration.io_callback_fixture import FakeIO


def test_simple_conditional():
    io = FakeIO([
        'var x int = 0',
        'if true { x = 2 }',
        'x'
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['2']
