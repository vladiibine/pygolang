keywords = (
    'FUNC',
    'RETURN',
)

tokens = keywords + \
         (
             'NAME',
             'NUMBER',
             'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EQUALS',
             'LPAREN', 'RPAREN',  # ( )
             'LBRACE', 'RBRACE',  # { }
             'LBRACKET', 'RBRACKET',  # [ ]
             'COMMA',  # ,

         )
