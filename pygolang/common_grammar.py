import enum


class KEYWORDS(enum.Enum):
    FUNC = 'FUNC'
    RETURN = 'RETURN'
    VAR = 'VAR'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    BOOL = 'BOOL'
    STRING = 'STRING'
    INT = 'INT'
    IF = 'IF'
    ELSE = 'ELSE'


class OPERATORS(enum.Enum):
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    TIMES = 'TIMES'
    DIVIDE = 'DIVIDE'
    MODULO = 'MODULO'

    EQUALS = 'EQUALS'  # Used in assignments!
    WALRUS = 'WALRUS'

    GREATER = 'GREATER'
    LESSER = 'LESSER'

    GREATEREQ = 'GREATEREQ'
    LESSEREQ = 'LESSEREQ'
    BOOLEQUALS = 'BOOLEQUALS'  # ==, used for boolean operations
    BOOLNOTEQUALS = 'BOOLNOTEQUALS'

    BOOLAND = 'BOOLAND'
    BOOLOR = 'BOOLOR'
    NOT = 'NOT'


keywords_tuple = tuple(e.name for e in KEYWORDS)


operators_tuple = tuple(e.name for e in OPERATORS)

tokens = keywords_tuple + \
         operators_tuple + \
         (
             'TYPE',  # what is this now? Surely this is wrong? NAME suffices
             'NAME',
             'LPAREN', 'RPAREN',  # ( )
             'LBRACE', 'RBRACE',  # { }
             'LBRACKET', 'RBRACKET',  # [ ]
             'COMMA',  # ,

         )
