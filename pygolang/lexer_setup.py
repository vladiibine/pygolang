import ply.lex as lex

# Tokens
from .common_grammar import tokens, keywords_tuple, SYNTAX


class PyGoLexer:
    ###
    # names here are used via reflection.
    # Don't just rename them, everything will break!
    tokens = tokens
    keywords = keywords_tuple

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MODULO = r'\%'
    t_EQUALS = r'='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_COMMA = r','
    t_DOT = r'\.'
    t_SEMICOLON = r';'

    # Boolean operators
    t_GREATER = '>'
    t_LESSER = '<'
    t_GREATEREQ = '>='
    t_LESSEREQ = '<='
    t_BOOLEQUALS = '=='
    t_BOOLNOTEQUALS = '!='

    t_BOOLAND = '&&'
    t_BOOLOR = r'\|\|'
    t_NOT = '!'

    # Ignored characters
    t_ignore = " \t"

    def __init__(self, side_effects):
        """

        :param pygolang.side_effects.SideEffects side_effects: Need this parameter
            to signal the creation of a new lexical scope when a "{" is reached
            Q: Do all situations where a "{" is read mark the beginning of
                a new lexical scope?
            A: I don't know any which don't
                >> UPDATE -> there might be situations, like with the
                interfaces, where we don't really mark new scopes....
                ..Ok, so I'll define some special parser rules for this
        :param pygolang.ast.TypeScopeStack type_scope_stack:
        """
        self.side_effects = side_effects
        lexer = lex.lex(module=self)
        self.lexer = LexerAdapter(lexer)

    def t_STRING(self, t):
        r""""(?:[^"\\]|\\.)*\""""
        t.value = t.value[1:-1]
        return t

    def t_WALRUS(self, t):
        r""":="""
        return t

    def t_NAME(self, t):
        r"""[a-zA-Z_][a-zA-Z0-9_]*"""
        if t.value.upper() in keywords_tuple:
            t.type = t.value.upper()

        return t

    def t_INT(self, t):
        r"""\d+"""
        try:
            t.value = int(t.value)
        except ValueError:
            self.side_effects.to_stdout("Integer value too large %d" % t.value)
            t.value = 0
        return t

    def t_NEWLINE(self, t):
        r"""\n+"""
        # TODO -> determine rules for when newlines are allowed
        #  So far I saw this:
        #  1. allowed after `(`, `[`, `{`, `,`
        #  2. required after statements (newline or `;`)
        #
        #  ...so given these rules, we should:
        # 1. Only emit newline when it's NOT right after these symbols: ([{,\n
        # 2. define newline and semicolon as symbols significant to the parser
        # 3. include in the definition of a statement that it should end in a
        #   statement terminator (newline or semicolon)
        #
        t.lexer.lineno += t.value.count("\n")
        if self.lexer.previous_token and \
                self.lexer.previous_token.type not in [
                    e.value for e in (
                        SYNTAX.NEWLINE,
                        SYNTAX.COMMA,
                        SYNTAX.LBRACE,
                        SYNTAX.LPAREN,
                        SYNTAX.LBRACKET,
                        SYNTAX.SEMICOLON,
                    )
                ]:
            return t

    def t_error(self, t):
        self.side_effects.to_stdout("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)


class LexerAdapter:
    def __init__(self, lexer):
        self.lexer = lexer
        self.previous_token = None

    def token(self):
        token = self.lexer.token()
        self.previous_token = token

        return token

    def input(self, *a, **kw):
        return self.lexer.input(*a, **kw)

