from pygolang.interpreter import main
from tests.integration.io_callback_fixture import FakeIO


def test_fmt_println():
    io = FakeIO([
        'import "fmt"',
        'fmt.Println(1)',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['1']
