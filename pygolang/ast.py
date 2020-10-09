class Func:
    def __init__(self, args, return_type, body):
        self.args = args
        self.return_type = return_type
        self.body = body


class FuncParams:
    def __init__(self, token):
        self.token = token


class FuncReturnType:
    def __init__(self, token):
        self.token = token


class FuncBody:
    def __init__(self, token):
        self.token = token
