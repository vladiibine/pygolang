from pygolang import ast
from pygolang.interpreter import main

from tests.fake_side_effects import FakeSideEffects


def test_parse_bool_literal():
    io = FakeSideEffects(["true", 'false'])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['true', 'false']


def test_parse_bool_explicit():
    io = FakeSideEffects(["var x bool = true"])

    scope = {}
    main(io, scope)

    assert not io.stderr
    assert not io.stdout
    assert 'x' in scope
    assert scope['x'][0] == ast.BoolLiteralTrue


def test_parse_string():
    io = FakeSideEffects([
        'var y string = "qwer"',
        'y',
        'x := "asdf"',
        'x',
        r'"\"asdf"',  # '"asdf' would be the python equivalent string
        '"a s d f"',
        '"asd\'f"',
        r'"a\nb"',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['"qwer"', '"asdf"', r'"\"asdf"', '"a s d f"', '"asd\'f"', r'"a\nb"']


def test_string_operators():
    io = FakeSideEffects([
        '"a" + "b"',
        r'"ab\""',

        '"a" < "b"',
        '"a" <= "b"',

        '"a" > "b"',
        '"a" >= "b"',

        '"" == ""',
        '" " != " "',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == [
        '"ab"', r'"ab\""',
        'true', 'true',
        'false', 'false',
        'true', 'false',
    ]
