from pygolang import ast
from pygolang.interpreter import main
from pygolang.stdlib import fmt
from tests.integration.io_callback_fixture import FakeIO


def test_import_fmt():
    io = FakeIO([
        'import "fmt"',
    ])

    state = {}
    main(io, state)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert 'fmt.Println' in state
    assert state['fmt.Println'][1] == fmt.Println.type
    assert state['fmt.Println'][0] == fmt.Println


def test_fmt_println():
    io = FakeIO([
        'import "fmt"',
        'fmt.Println(1)',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['1']

