from pygolang.side_effects import SideEffects
from pygolang.errors import StopPyGoLangInterpreterError


class FakeSideEffects(SideEffects):
    def __init__(self, stdin_as_str_list, fake_files=(), environ=None):
        """
        :param list[str] stdin_as_str_list: list(or iterable) of strings, to
            simulate the lines from stdin
        :param list[dict] fake_files: Dict containing the 'path' and 'content'
            keys. Will be used instead of real files
        """
        self.stdin = stdin_as_str_list
        self.stdout = []
        self.stderr = []
        self.sleep_list = []  # for recording time.Sleep calls
        self.input_generator = None

        # {'path': {'type': <"f" or "d", marking a file or directory>, 'content': "content string"}}
        self.files = self.initialize_file_system(fake_files)
        self.environ = environ or {}

    def initialize_file_system(self, fake_files):
        files = {}

        for filespec in fake_files:
            files[filespec['path']] = {
                'type': 'f',
                'content': filespec['content']
            }

            if '/' not in filespec['path']:
                # No parent folders, we're done
                continue

            parent_folders = filespec['path'].rsplit('/', 1)[0].split('/')
            for end_idx in range(1, len(parent_folders) + 1):
                folder_to_create = parent_folders[0: end_idx]
                files['/'.join(folder_to_create)] = {
                    'type': 'd',
                    'content': None
                }

        return files






    def from_stdin(self):
        def iterate_over_stdin():
            for line in self.stdin:
                yield line

            raise StopPyGoLangInterpreterError

        if not self.input_generator:
            self.input_generator = iterate_over_stdin()

        return next(self.input_generator)

    def to_stdout(self, stuff):
        self.stdout.append(stuff)

    def to_stderr(self, stuff):
        self.stderr.append(stuff)

    def sleep(self, interval):
        self.sleep_list.append(interval)

    def interpreter_prompt(self):
        pass

    def newline(self):
        pass

    def format_stderr_for_debugging(self):
        return '\n'.join(str(e) for e in self.stderr)

    def get_environ(self, param):
        return self.environ.get(param)

    def isdir(self, path):
        return self.files.get(path, {}).get('type') == 'd'

    def list_files_in_dir(self, folder):
        result = []
        for filekey, filespec in self.files.items():
            if not filekey.startswith(folder):
                continue

            if filespec['type'] != 'f':
                continue

            if '/' in filekey[len(folder) + 1:]:
                # File path contains further subfolders
                continue

            result.append(filekey)

        return result

    def read_file(self, filename):
        return self.files[filename]['content']







