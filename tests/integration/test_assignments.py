from pygolang import ast
from pygolang.interpreter import main

from tests.integration.fake_side_effects import FakeSideEffects


def test_can_assign_bool_to_declared_variable():
    io = FakeSideEffects(["var x bool", "x = true"])
    state = {}

    main(io, state)

    assert state['x'][0] == ast.BoolLiteralTrue


def test_cant_assign_int_literal_to_bool_variable():
    pass


def test_setting_default_value_for_declared_bool():
    pass
