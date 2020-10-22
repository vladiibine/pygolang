from tests.fake_side_effects import FakeSideEffects


class TestInitializeFileSystem:
    def test_initializes_simple_file(self):
        side_effects = FakeSideEffects([], [{'path': 'a', 'content': 'x'}])

        assert side_effects.files == {
            'a': {
                'type': 'f',
                'content': 'x'
            }
        }

    def test_initializes_file_with_folders(self):
        side_effects =FakeSideEffects([], [{'path': 'a/b/c', 'content': 'x'}])

        assert side_effects.files == {
            'a': {'type': 'd', 'content': None},
            'a/b': {'type': 'd', 'content': None},
            'a/b/c': {'type': 'f', 'content': 'x'}
        }
