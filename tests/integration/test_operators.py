from pygolang.interpreter import main

from tests.integration.io_callback_fixture import FakeIO


def test_plus():
    io = FakeIO(['x=1+1'])

    state = {}
    main(io, state)

    assert not io.stdout
    assert not io.stderr

    assert 'x' in state
    assert state['x'] == 2
