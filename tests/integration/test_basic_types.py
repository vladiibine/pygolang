from pygolang import ast
from pygolang.repl import main
from pygolang.runtime.namespaces import GlobalNamespace, PackageNamespace

from tests.fake_side_effects import FakeSideEffects


def test_parse_bool_literal():
    io = FakeSideEffects(["true", 'false'])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['true', 'false']


def test_parse_bool_explicit():
    io = FakeSideEffects(["var x bool = true"])

    scope = {}
    main(io, lambda: GlobalNamespace({'main': PackageNamespace(scope)}))

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


def test_cant_assign_incompatible_types():
    side_effects = FakeSideEffects([
        'var x bool',
        'x = "asf"',
    ])

    main(side_effects)

    assert side_effects.stderr
    assert """Can't assign type 'string' to variable 'x' of type 'bool'""" \
        in side_effects.stderr[1], side_effects.format_stderr_for_debugging()


def test_cant_assign_incompatible_types_from_function_call():
    side_effects = FakeSideEffects([
        'var x bool',
        'func asdf()int{return 4}',
        'x = asdf()'
    ])

    main(side_effects)

    assert side_effects.stderr
    assert """Can't assign type 'int' to variable 'x' of type 'bool'""" in \
           side_effects.stderr[1], side_effects.format_stderr_for_debugging()
