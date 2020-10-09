from pygolang.interpreter import main

from tests.integration.io_callback_fixture import FakeIO


def test_plus():
    io = FakeIO(['1+1'])

    main(io)

    assert len(io.stdout) == 1

    assert io.stdout[0] == 2
