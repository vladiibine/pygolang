import importlib

from pygolang import ast


class Importer:
    def __init__(self, side_effects):
        """
        :param pygolang.side_effects.SideEffects side_effects:
        """
        self.side_effects = side_effects

    def import_from_stdlib(self, import_string):
        """Import names from the standard library
        (functionality re-implemented in python)

        :param str import_string:
        :rtype: list[tuple[str,pygolang.ast.Type,object]]
        """
        new_variables = []
        try:
            module = importlib.import_module(
                f'.stdlib.{import_string}', 'pygolang'
            )

            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, ast.NativeFunction):
                    qualified_name = '.'.join([import_string, name])
                    new_variables.append((qualified_name, obj.type, obj))
        except ImportError:
            pass

        return new_variables

    def import_from_modules(self, import_string):
        """
        :param str import_string:
        :return: A list of strings, representing the statements in the imported
            package (all the

        :rtype: list[str]
        """
        # If that doesn't work, try to import from files we have access to
        # 1. get a list of initial folders to check in
        # 2. in all the initial folders, look for folders containing go.mod
        #   files
        # 3. the first go.mod file declaring the name `module <name-here>`
        #   we're looking for will give us the folder to next search for
        #   packages
        # 4. given the folder determined earlier, we must create a package
        #   scope, and evaluate all the files in it in this scope
        # 5. After all files have been evaluated, export all their names
        #   to the initial package's scope
        result = []

        # TODO -> implement

        return result
