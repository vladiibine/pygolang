from pygolang.interpreter import main
from tests.fake_side_effects import FakeSideEffects


def test_grouping_expressions_in_conditionals():
    io = FakeSideEffects([
        'x:=1',
        'if (!(1 == 2) && !(1 != 1)){x = 2}',
        'x',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['2']


def test_assignment_from_groupings():
    io = FakeSideEffects([
        'x:=(((1)))',
        'x',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['1']
