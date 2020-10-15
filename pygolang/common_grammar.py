keywords = (
    'FUNC',
    'RETURN',
    'VAR',
    'TRUE',
    'FALSE',
    'BOOL',
)

operators = (
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'EQUALS', 'WALRUS',
)

tokens = keywords + \
         operators + \
         (
             'TYPE',
             'NAME',
             'NUMBER',
             'LPAREN', 'RPAREN',  # ( )
             'LBRACE', 'RBRACE',  # { }
             'LBRACKET', 'RBRACKET',  # [ ]
             'COMMA',  # ,

         )
