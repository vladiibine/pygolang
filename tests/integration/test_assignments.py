from pygolang import ast
from pygolang.repl import main
from pygolang.runtime.namespaces import GlobalNamespace, PackageNamespace

from tests.fake_side_effects import FakeSideEffects


def test_can_assign_bool_to_declared_variable():
    io = FakeSideEffects(["var x bool", "x = true"])
    state = {}

    main(io, lambda: GlobalNamespace({'main': PackageNamespace(state)}))

    assert not io.stderr, io.format_stderr_for_debugging()
    assert state['x'][0] == ast.BoolLiteralTrue


def test_cant_assign_int_literal_to_bool_variable():
    pass


def test_setting_default_value_for_declared_bool():
    pass
