import os
import sys
import time


class SideEffects:
    def __init__(self, stdout=None, stderr=None, stdin=None):
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr
        self.stdin = stdin or sys.stdin
        # ...add all file descriptors here
        # for all files, for all sockets, for everything that's IO

    def to_stdout(self, stuff):
        self.stdout.write(str(stuff))
        self.stdout.flush()

    def to_stderr(self, stuff):
        self.stderr.write(str(stuff))
        self.stderr.flush()

    def from_stdin(self):
        return self.stdin.readline().lstrip('\n')

    def sleep(self, interval):
        time.sleep(interval)

    def interpreter_prompt(self):
        self.to_stdout("pygo> ")

    def newline(self):
        self.to_stdout('\n')

    def get_environ(self, param):
        return os.environ.get(param)

    def isdir(self, path):
        return os.path.isdir(path)

    def list_files_in_dir(self, folder):
        return next(os.walk(folder))[2]

    def read_file(self, filename):
        with open(filename) as f:
            return f.read()
