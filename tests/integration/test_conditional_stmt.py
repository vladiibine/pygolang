from pygolang import ast
from pygolang.repl import main

from tests.fake_side_effects import FakeSideEffects


def test_simple_conditional():
    io = FakeSideEffects([
        'var x int = 0',
        'if true { x = 2 }',
        'x'
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['2']


def test_simple_if_conditional_twice():
    io = FakeSideEffects([
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
    io = FakeSideEffects([
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
    io = FakeSideEffects([
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


def test_chained_if_statements_no_final_else_with_true_at_the_end():
    io = FakeSideEffects([
        'x := 1',
        'if false {x = 2} else if true { x = 3}',
        'x',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['3']


def test_chained_if_statements_with_true_in_the_middle_no_final_else():
    io = FakeSideEffects([
        'x := 1',
        'if false {x = 2} else if true { x = 3} else if true { x = 4}',
        'x',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['3']


def test_chained_if_statements_with_true_in_the_middle_with_final_else():
    io = FakeSideEffects([
        'x := 1',
        'if false {x = 2} else if true { x = 3} else if true { x = 4} else {x = 5}',
        'x',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['3']


def test_else_block_simple_if_statement():
    io = FakeSideEffects([
        'x := 1',
        'if false {x = 2} else {x = 3}',
        'x',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['3']


def test_chained_if_with_final_else_fallback_block_executing():
    io = FakeSideEffects([
        'x := 1',
        'if false {x = 2} else if false { x = 3} else if false { x = 4} else {x = 5}',
        'x',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['5']


def test_no_block_is_executed_except_for_the_one_with_an_expression_evaluating_to_true():
    io = FakeSideEffects([
        'x := 1',
        'y := 1',
        'z := 1',
        'if false {x = 2} else if false { y = 3} else if false { z = 4} else {x = 5}',
        'x',
        'y',
        'z',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['5', '1', '1']


def test_conditionals_work_with_boolean_expressions():
    io = FakeSideEffects([
        'x := 1',
        'if x == 1 {x=2}',
        'x',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['2']


def test_conditionals_work_with_boolean_operators():
    io = FakeSideEffects([
        'x := 1',
        'if x == 1 && x != 2 {x = 2}',
        'x',
        'if 1 == 2 || 2 != 2 || 1 == 1 {x = 3}',
        'x'
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['2', '3']
