import importlib
import os

from pygolang import ast


class Importer:
    """
    More about how imports and the $GOPATH env var are related here:
        https://golang.org/cmd/go/#hdr-GOPATH_environment_variable

    """
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

    def import_from_modules(self, import_path):
        """
        :param str import_path: Strings like "folder1" or "folder1/folder2"
            (or nested an arbitrary number of levels), representing
            golang import paths
        :return: a list of strings, representing the contents of all the files
            in the package

        :rtype: types.Iterator[str]
        """
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

        raise NotImplementedError

        return result

    # TODO -> very easy and beneficial to cache this method
    def import_from_gopath(self, import_path):
        """Implements the older dependency resolution mechanism

        :param str import_path:

        1. Looks at $GOPATH
        2. Every folder in $GOPATH is a package, recursively
        3. All files in that package must specify as package name the folder
            where they live
        4. Imports specify the full path of a folder, relative to any folder
            in the $GOPATH

        Example1:
        $ export GOPATH=/some/path
        $cat /some/path/src/pkg1/asdf.go
        package pkg1

        func Asdf() string {return "Asdf"}

        $ cat /some/path/src/pkf1/zxcv.go
        package pkg1

        func Zxcv() string {return "Zxcv"}

        $ pwd
        /other/path
        $ cat /other/path/file.go
        package main

        import (
            "pkg1"
            "fmt"
        )

        func main(){
            fmt.Println(pkg1.Asdf())
            fmt.Println(pkg1.Zxcv())
        }

        $ go build file.go  # this should work


        :param import_string:
        :return:
        """
        result = []

        # 1. Get a list of folders where we can check
        folder_list = self.side_effects.get_environ('GOPATH').split(':')
        folder_list = folder_list or [os.path.expanduser('~/go')]

        for folder in folder_list:
            candidate_folder = os.path.join(folder, 'src', import_path)
            # if not os.path.isdir(candidate_folder):
            if not self.side_effects.isdir(candidate_folder):
                continue

            for filename in self.side_effects.list_files_in_dir(candidate_folder):
                # All files in the candidate folder
                if filename.endswith('.go'):
                    result.append(self.side_effects.read_file(filename))

        return result
