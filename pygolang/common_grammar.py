keywords = (
    'FUNC',
    'RETURN',
)

operators = (
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EQUALS',
)

tokens = keywords + \
         operators + \
         (
             'NAME',
             'NUMBER',
             'LPAREN', 'RPAREN',  # ( )
             'LBRACE', 'RBRACE',  # { }
             'LBRACKET', 'RBRACKET',  # [ ]
             'COMMA',  # ,

         )
