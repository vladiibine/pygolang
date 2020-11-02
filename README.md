# pygolang
golang compiler written in python

# Installation
I know, it's very rough atm, but might be simplified in the future
```bash
$ git clone git@github.com:vladiibine/pygolang.git
$ cd pygolang
$ python -m venv pygolang-ve
$ source ./pygolang-ve/bin/activate
$ pip install -r requirements.txt
```

# Usage
```bash
$ python -m pygolang.repl
```

Examples
--------
```
pygo> 1
1
pygo> 1+2
3
pygo> x=4

pygo> x
4
pygo> x+4
8
pygo> func asdf(x int)int{return 3}

pygo> asdf(5)
3
```
