from pygolang.ast_runner.importer import Importer
from tests.fake_side_effects import FakeSideEffects


class TestImportFromModules:
    def test_imports_dummy_variable_from_single_pkg_file(self):
        side_effects = FakeSideEffects(
            ['import "asfd/modulex/pkg1"'],
            [
                {
                    'path': 'asdf/modulex/go.mod',
                    'content': 'module asdf'
                },
                {
                    'path': 'asdf/modulex/pkg1/file1.go',
                    'content': 'x'
                },
            ]
        )

        importer = Importer(side_effects)

        result = importer.import_from_modules("asdf/modulex/pkg1")

        assert list(result) == ['x']


class TestImportFromGopath:
    def test_imports_single_file(self):
        side_effects = FakeSideEffects(
            ['import "asfd/modulex/pkg1"'],
            [
                {
                    'path': 'asdf/path/src/pkg1/file1.go',
                    'content': 'x'
                },
            ],
            {'GOPATH': 'asdf/path'}
        )

        importer = Importer(side_effects)

        result = importer.import_from_gopath('pkg1')

        assert result == ['x']

    def test_imports_2_files(self):
        side_effects = FakeSideEffects(
            ['import "asfd/modulex/pkg1"'],
            [
                {
                    'path': 'asdf/path/src/pkg1/file1.go',
                    'content': 'x'
                },
                {
                    'path': 'asdf/path/src/pkg1/file2.go',
                    'content': 'y'
                },
            ],
            {'GOPATH': 'asdf/path'}
        )

        importer = Importer(side_effects)

        result = importer.import_from_gopath('pkg1')

        assert result == ['x', 'y']
