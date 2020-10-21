import sys


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

    def interpreter_prompt(self):
        self.to_stdout("pygo> ")

    def newline(self):
        self.to_stdout('\n')