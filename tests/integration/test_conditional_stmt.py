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


def test_simple_if_conditional_twice():
    io = FakeIO([
        'x := 1',
        'x',
        'if true {x = 2}',
        'x',
        'if false {x = 3}',
        'x',
        'if true {x = 4}',
        'x',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['1', '2', '2', '4']


def test_if_with_expression_from_name():
    io = FakeIO([
        't := true',
        'f := false',
        'x := 1',
        'x',
        'if t { x = 2}',
        'x',
        'if f { x = 3 }',
        'x',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['1', '2', '2']


def test_if_with_expression_from_func_call():
    io = FakeIO([
        'func t()bool{return true}',
        'func f()bool{return false}',
        'x := 0',
        'x',
        'if t() {x = 1}',
        'x',
        'if f() {x = 2}',
        'x',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['0', '1', '1']
