from pygolang.interpreter import main
from tests.integration.io_callback_fixture import FakeIO


def test_goroutines_1():
    io = FakeIO([
        'import "fmt"',
        'import "time"',
        """
        func sleepThenPrint() int {
            time.Sleep(1)
            fmt.Println(1)
        }
        """,
        'go sleepThenPrint()',
        'fmt.Println(2)',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['2', '1']
