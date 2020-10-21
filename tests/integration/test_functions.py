from pygolang import ast
from pygolang.interpreter import main

from tests.integration.fake_side_effects import FakeSideEffects


def test_basic_syntax():
    io = FakeSideEffects([
        # "name1 = 3",
        # "name2 = 4",
        """
func asdf(name1 int)int{
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
    assert isinstance(state['asdf'][0], ast.FuncCreation)

    # yeah... hardcoding this repr string here for now.
    # It's kind of cumbersome to create this string, so it's just fine like
    # this for now.
    assert state['asdf'][1].repr == 'func (int) int'


def test_calling_function_containing_only_a_return_statement():
    io = FakeSideEffects([
        """func asdf( name1 int)int{return 133}""",
        """var x int = asdf(3)"""
    ])
    state = {}

    main(io, state)

    assert 'x' in state
    assert state['x'][0] == ast.Int(133)


def test_calling_function_that_returns_an_argument():
    io = FakeSideEffects([
        """func asdf(name1 int)int{return name1}""",
        """var x int = asdf(3)"""
    ])
    state = {}

    main(io, state)

    assert 'x' in state
    assert state['x'][0] == ast.Int(3)


def test_calling_function_without_params():
    io = FakeSideEffects([
        "func x()int{return 2}",
        "x()"
    ])
    state = {}

    main(io, state)

    assert io.stdout == ['2']


def test_calling_function_that_sums_its_arguments():
    io = FakeSideEffects([
        "func add(x int, y int) int {return x + y }",
        "add(1,2)"
    ])

    main(io)

    assert io.stdout == ['3']


def test_function_that_uses_global_scope_and_arguments_to_produce_result_qm7():
    io = FakeSideEffects([
        "var z int = 4",
        "func add(x int, y int) int {return x + y + z}",
        "add(1, 2)",
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()

    assert io.stdout == ['7']
