from pygolang.interpreter import main

from tests.integration.io_callback_fixture import FakeIO


def test_plus():
    io = FakeIO(['1+1'])

    state = {}

    main(io, state)

    assert io.stdout
    assert io.stdout == [2]
    assert not io.stderr
