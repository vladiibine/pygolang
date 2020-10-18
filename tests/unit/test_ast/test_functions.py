from pygolang import common_grammar
from pygolang.ast import initialize_operator_type_map


class TestInitializeOperatorTypeMap:
    def test_creates_binary_operator_map(self):
        result = initialize_operator_type_map([
            [common_grammar.OPERATORS.PLUS, 1, 2, 'return_type', 'func']
        ])

        assert result == {
            common_grammar.OPERATORS.PLUS.value: {
                1: {
                    2: ['return_type', 'func']
                }
            }
        }

    def test_creates_unary_operator_map(self):
        result = initialize_operator_type_map([
            [common_grammar.OPERATORS.PLUS, 1, 'return_type', 'funcxx']
        ])

        assert result == {
            common_grammar.OPERATORS.PLUS.value: {
                1: ['return_type', 'funcxx']
            }
        }
