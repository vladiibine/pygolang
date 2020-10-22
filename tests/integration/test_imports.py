from pygolang import ast
from pygolang.interpreter import main
from pygolang.stdlib import fmt
from tests.fake_side_effects import FakeSideEffects


def test_import_fmt():
    io = FakeSideEffects([
        'import "fmt"',
    ])

    state = {}
    main(io, state)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert 'fmt.Println' in state
    assert state['fmt.Println'][1] == fmt.Println.type
    assert state['fmt.Println'][0] == fmt.Println


def test_fmt_println():
    io = FakeSideEffects([
        'import "fmt"',
        'fmt.Println(1)',
    ])

    main(io)

    assert not io.stderr, io.format_stderr_for_debugging()
    assert io.stdout == ['1']


def test_time_sleep():
    side_effects = FakeSideEffects([
        'import "time"',
        """
        func f(x int) int {
            time.Sleep(x)
        }
        """,
        'f(2)',
    ])

    main(side_effects)

    assert not side_effects.stderr, side_effects.format_stderr_for_debugging()
    assert side_effects.sleep_list == [2]
    assert not side_effects.stdout


def test_import_module_packages():
    side_effects = FakeSideEffects([
        'import "modulex/pkg1"',
        'pkg1.Func1()',
    ], [
        {
            'path': './modulex/pkg1/f1.go',
            'content': '''
                package pkg1; 
                func Func1() string {return "Hello World!"}
            '''
        },
        {'path': './modulex/go.mod', 'content': 'module modulex'}
    ])

    main(side_effects)

    assert not side_effects.stderr, side_effects.format_stderr_for_debugging()
    assert side_effects.stdout == ['"Hello World!"']
