from pygolang import ast
from pygolang.interpreter import main

from tests.integration.io_callback_fixture import FakeIO


def test_basic_syntax():
    io = FakeIO([
        # "name1 = 3",
        # "name2 = 4",
        """
func asdf(name1 int)name2{
    1
}
        """
    ])

    state = {}
    main(io, program_state=state)

    # A function was just declared. Nothing printed
    assert not io.stderr
    assert not io.stdout
    assert len(state) == 1
    assert 'asdf' in state
    assert isinstance(state['asdf'], ast.Func)

