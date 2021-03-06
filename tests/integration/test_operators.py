from pygolang import ast
from pygolang.interpreter import main

from tests.integration.io_callback_fixture import FakeIO


def test_int_arithmetic_operators():
    io = FakeIO([
        '1+1',
        '1-1',
        '2*3',
        '3/2',
        '17 % 13',
    ])

    state = {}

    main(io, state)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['2', '0', '6', '1', '4']
    assert not io.stderr


def test_walrus_plus():
    io = FakeIO(['x := 1'])

    state = {}

    main(io, state)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert state['x'][0] == ast.Int(1)
    assert state['x'][1] == ast.IntType


def test_int_boolean_operators():
    io = FakeIO([
        '1 > 0',
        '1 < 0',

        '1 >= 1',
        '1 >= 2',

        '1 == 1',
        '1 == 2',
        
        '1 != 1',
        '1 != 2',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == [
        'true', 'false',
        'true', 'false',
        'true', 'false',
        'false', 'true',
    ]


def test_not_operator_fails_like_in_golang():
    io = FakeIO([
        'x := 1',
        'if ! 1 == 2 {x = 2}',
        'x',
    ])

    main(io)

    assert io.stderr
    assert 'Invalid operation (!)' in io.stderr[1]
    assert io.stdout == ['1']

