from pygolang.ast_runner.importer import Importer
from tests.integration.fake_side_effects import FakeSideEffects


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
                    'content': '''
                    package pkg1
                    
                    func YayFunc(a,b int) string { return "Hello world!"}
                    '''
                }
            ]
        )

        importer = Importer(side_effects)

        result = importer.import_from_modules("asdf/modulex/pkg1")
