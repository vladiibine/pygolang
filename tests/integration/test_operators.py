from pygolang import ast
from pygolang.repl import main
from pygolang.runtime.namespaces import GlobalNamespace, PackageNamespace

from tests.fake_side_effects import FakeSideEffects


def test_int_arithmetic_operators():
    io = FakeSideEffects([
        '1+1',
        '1-1',
        '2*3',
        '3/2',
        '17 % 13',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['2', '0', '6', '1', '4']
    assert not io.stderr


def test_walrus_plus():
    io = FakeSideEffects(['x := 1'])

    state = {}

    main(io, lambda: GlobalNamespace({'main': PackageNamespace(state)}))

    assert not io.stderr, io.format_stderr_for_debugging()
    assert state['x'][0] == ast.Int(1)
    assert state['x'][1] == ast.IntType


def test_int_boolean_operators():
    io = FakeSideEffects([
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
    io = FakeSideEffects([
        'x := 1',
        'if ! 1 == 2 {x = 2}',
        'x',
    ])

    main(io)

    assert io.stderr
    assert 'Invalid operation (!)' in io.stderr[1]
    assert io.stdout == ['1']

