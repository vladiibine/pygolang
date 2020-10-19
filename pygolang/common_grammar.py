import enum


class KEYWORDS(enum.Enum):
    BOOL = 'BOOL'
    ELSE = 'ELSE'
    FALSE = 'FALSE'
    FUNC = 'FUNC'
    IF = 'IF'
    INT = 'INT'
    IMPORT = 'IMPORT'
    RETURN = 'RETURN'
    STRING = 'STRING'
    TRUE = 'TRUE'
    VAR = 'VAR'


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


class SYNTAX(enum.Enum):
    LPAREN = 'LPAREN'  # (
    RPAREN = 'RPAREN'  # )
    LBRACE = 'LBRACE'  # {
    RBRACE = 'RBRACE'  # }
    LBRACKET = 'LBRACKET'  # [
    RBRACKET = 'RBRACKET'  # ]

    DOUBLEQUOTE = 'DOUBLEQUOTE'  # "
    SINGLEQUOTE = 'SINGLEQUOTE'  # '

    COMMA = 'COMMA'  # ,


keywords_tuple = tuple(e.name for e in KEYWORDS)
operators_tuple = tuple(e.name for e in OPERATORS)
syntax_tuple = tuple(e.name for e in SYNTAX)

tokens = keywords_tuple + \
         operators_tuple + \
         syntax_tuple + \
         (
             'TYPE',  # what is this now? Surely this is wrong? NAME suffices
             'NAME',
         )
