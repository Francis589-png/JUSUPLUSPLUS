"""
Jusu++ Parser - Converts tokens to Abstract Syntax Tree (AST)
"""

class ASTNode:
    """A node in the Abstract Syntax Tree"""
    def __init__(self, node_type, **kwargs):
        self.type = node_type
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        attrs = []
        for key, value in self.__dict__.items():
            if key != 'type':
                attrs.append(f"{key}={repr(value)}")
        return f"{self.type}({', '.join(attrs)})"

class Parser:
    """Parses tokens into an AST"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0  # Current token index

    # Helper to get current token without side-effects (useful for source locations)
    def current_token(self):
        return self.peek()

    
    def parse(self):
        """Parse the tokens into a program AST"""
        statements = []
        
        while not self.is_at_end():
            # Skip any leading newlines or blank lines
            self.consume_newlines()
            if self.is_at_end():
                break

            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.consume_newlines()
        
        return statements
    
    def parse_statement(self):
        """Parse a single statement"""
        if self.match('KEYWORD', 'say'):
            return self.parse_say_statement()
        elif self.match('KEYWORD', 'if'):
            return self.parse_if_statement()
        elif self.match('KEYWORD', 'function'):
            return self.parse_function_declaration()
        elif self.match('KEYWORD', 'return'):
            return self.parse_return_statement()
        elif self.check('IDENTIFIER') and self.peek_next_is(('KEYWORD', 'is'), ('OPERATOR', '=')):
            return self.parse_assignment()
        else:
            # Try to parse as expression statement
            expr = self.parse_expression()
            self.consume('NEWLINE')
            return ASTNode('ExpressionStatement', expression=expr)
    
    def parse_say_statement(self):
        """Parse a say statement: say expression"""
        # We already consumed 'say' (previous() is the 'say' token)
        start = self.previous()
        expr = self.parse_expression()
        self.consume('NEWLINE')
        return ASTNode('SayStatement', expression=expr, line=start.line, column=start.column)
    
    def parse_assignment(self):
        """Parse variable assignment: name is value or name = value"""
        name = self.advance()  # Get variable name (Token)
        start = name
        
        # Check for 'is' or '='
        if self.match('KEYWORD', 'is'):
            pass  # 'is' is consumed
        elif self.match('OPERATOR', '='):
            pass  # '=' is consumed
        else:
            self.error("Expected 'is' or '=' after variable name")
        
        value = self.parse_expression()
        self.consume('NEWLINE')
        return ASTNode('Assignment', name=name.value, value=value, line=start.line, column=start.column)
    
    def parse_expression(self):
        """Parse an expression (supports comparisons)"""
        return self.parse_comparison()
    
    def parse_comparison(self):
        """Parse comparison operators: ==, !=, <, >, <=, >="""
        expr = self.parse_addition()
        while self.match('OPERATOR', '==') or self.match('OPERATOR', '!=') or \
              self.match('OPERATOR', '<') or self.match('OPERATOR', '>') or \
              self.match('OPERATOR', '<=') or self.match('OPERATOR', '>='):
            operator = self.previous()
            right = self.parse_addition()
            expr = ASTNode('BinaryExpression', left=expr, operator=operator.value, right=right)
        return expr
    
    def parse_addition(self):
        """Parse addition/subtraction: + or -"""
        expr = self.parse_multiplication()
        
        while self.match('OPERATOR', '+') or self.match('OPERATOR', '-'):
            operator = self.previous()
            right = self.parse_multiplication()
            expr = ASTNode('BinaryExpression',
                          left=expr, operator=operator.value, right=right)
        
        return expr
    
    def parse_multiplication(self):
        """Parse multiplication/division: * or /"""
        expr = self.parse_primary()
        
        while self.match('OPERATOR', '*') or self.match('OPERATOR', '/'):
            operator = self.previous()
            right = self.parse_primary()
            expr = ASTNode('BinaryExpression',
                          left=expr, operator=operator.value, right=right)
        
        return expr
    
    def parse_primary(self):
        """Parse primary expressions: literals, identifiers, groups"""
        if self.match('NUMBER'):
            tok = self.previous()
            return ASTNode('NumberLiteral', value=float(tok.value), line=tok.line, column=tok.column)
        elif self.match('STRING'):
            tok = self.previous()
            return ASTNode('StringLiteral', value=tok.value, line=tok.line, column=tok.column)
        elif self.match('IDENTIFIER'):
            # Handle chained identifiers like a.b.c
            ident_tok = self.previous()
            name_parts = [ident_tok.value]
            while self.match('PUNCTUATION', '.'):
                if self.match('IDENTIFIER'):
                    name_parts.append(self.previous().value)
                else:
                    self.error("Expected identifier after '.'")
            full_name = '.'.join(name_parts)

            # Potential function call: IDENTIFIER '(' args ')'
            if self.match('PUNCTUATION', '('):
                args = []
                # Handle empty argument list
                if not self.check('PUNCTUATION', ')'):
                    while True:
                        args.append(self.parse_expression())
                        if self.match('PUNCTUATION', ')'):
                            break
                        self.consume('PUNCTUATION', ',')
                else:
                    # consume the closing parenthesis for empty arg list
                    self.consume('PUNCTUATION', ')')
                return ASTNode('CallExpression', callee=full_name, arguments=args, line=ident_tok.line, column=ident_tok.column)
            return ASTNode('Identifier', name=full_name, line=ident_tok.line, column=ident_tok.column)
        elif self.match('KEYWORD', 'true'):
            return ASTNode('BooleanLiteral', value=True)
        elif self.match('KEYWORD', 'false'):
            return ASTNode('BooleanLiteral', value=False)
        elif self.match('PUNCTUATION', '('):
            expr = self.parse_expression()
            self.consume('PUNCTUATION', ')')
            return expr
        elif self.match('PUNCTUATION', '{'):
            # Object literal: { key: value, ... }
            pairs = []
            if not self.check('PUNCTUATION', '}'):
                while True:
                    # keys are usually strings or identifiers
                    if self.match('STRING'):
                        key = self.previous().value
                    elif self.match('IDENTIFIER'):
                        key = self.previous().value
                    else:
                        self.error('Expected string or identifier for object key')
                    self.consume('PUNCTUATION', ':')
                    value = self.parse_expression()
                    pairs.append((key, value))
                    if self.match('PUNCTUATION', '}'):
                        break
                    self.consume('PUNCTUATION', ',')
            else:
                self.consume('PUNCTUATION', '}')
            return ASTNode('ObjectLiteral', pairs=pairs)
        elif self.match('PUNCTUATION', '['):
            # Array literal: [a, b, c]
            elements = []
            if not self.check('PUNCTUATION', ']'):
                while True:
                    elements.append(self.parse_expression())
                    if self.match('PUNCTUATION', ']'):
                        break
                    self.consume('PUNCTUATION', ',')
            else:
                self.consume('PUNCTUATION', ']')
            return ASTNode('ArrayLiteral', elements=elements)
        else:
            self.error(f"Unexpected token: {self.peek().type} '{self.peek().value}'")

    def parse_if_statement(self):
        """Parse an if statement with optional else and block using 'end' to finish"""
        # 'if' has been consumed (previous() is the 'if' token)
        start = self.previous()
        condition = self.parse_expression()
        self.consume('PUNCTUATION', ':')
        self.consume('NEWLINE')
        then_branch = self.parse_block()
        else_branch = None
        if self.match('KEYWORD', 'else'):
            self.consume('PUNCTUATION', ':')
            self.consume('NEWLINE')
            else_branch = self.parse_block()
        return ASTNode('IfStatement', condition=condition, then_branch=then_branch, else_branch=else_branch, line=start.line, column=start.column)

    def parse_function_declaration(self):
        """Parse a function declaration: function name(args): <body> end"""
        # 'function' already consumed; use previous() for location
        start = self.previous()
        name_token = self.consume('IDENTIFIER')
        name = name_token.value
        self.consume('PUNCTUATION', '(')
        params = []
        if not self.check('PUNCTUATION', ')'):
            while True:
                p = self.consume('IDENTIFIER')
                params.append(p.value)
                if self.match('PUNCTUATION', ')'):
                    break
                self.consume('PUNCTUATION', ',')
        else:
            self.consume('PUNCTUATION', ')')
        self.consume('PUNCTUATION', ':')
        self.consume('NEWLINE')
        body = self.parse_block()
        return ASTNode('FunctionDeclaration', name=name, params=params, body=body, line=start.line, column=start.column)

    def parse_return_statement(self):
        """Parse a return statement"""
        # 'return' is consumed
        start = self.previous()
        if self.check('NEWLINE'):
            self.consume('NEWLINE')
            return ASTNode('ReturnStatement', value=None, line=start.line, column=start.column)
        value = self.parse_expression()
        self.consume('NEWLINE')
        return ASTNode('ReturnStatement', value=value, line=start.line, column=start.column)

    def parse_block(self):
        """Parse a block of statements until 'end' or 'else'"""
        statements = []
        while not self.is_at_end() and not (self.check('KEYWORD', 'end') or self.check('KEYWORD', 'else')):
            self.consume_newlines()
            if self.check('KEYWORD', 'end') or self.check('KEYWORD', 'else') or self.is_at_end():
                break
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.consume_newlines()
        # Consume 'end' if present
        if self.match('KEYWORD', 'end'):
            if self.check('NEWLINE'):
                self.consume('NEWLINE')
        return statements
    
    # ====== HELPER METHODS ======
    
    def match(self, token_type, value=None):
        """Check if current token matches, consume if true"""
        if self.check(token_type, value):
            self.advance()
            return True
        return False
    
    def check(self, token_type, value=None):
        """Check if current token matches without consuming"""
        if self.is_at_end():
            return False
        token = self.peek()
        if token.type != token_type:
            return False
        if value is not None and token.value != value:
            return False
        return True
    
    def peek_next_is(self, *token_specs):
        """Check if next token matches any of the given specs"""
        if self.current + 1 >= len(self.tokens):
            return False
        next_token = self.tokens[self.current + 1]
        
        for token_type, value in token_specs:
            if next_token.type == token_type and next_token.value == value:
                return True
        return False
    
    def advance(self):
        """Move to next token and return it"""
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def peek(self):
        """Look at current token without consuming"""
        return self.tokens[self.current]
    
    def previous(self):
        """Get the previous token"""
        return self.tokens[self.current - 1]
    
    def consume(self, token_type, value=None):
        """Consume a token, error if it doesn't match"""
        if self.check(token_type, value):
            return self.advance()
        token = self.peek()
        self.error(f"Expected {token_type} '{value}' but got {token.type} '{token.value}'")
    
    def consume_newlines(self):
        """Consume any number of newlines"""
        while self.match('NEWLINE'):
            pass
    
    def is_at_end(self):
        """Check if we've consumed all tokens"""
        return self.peek().type == 'EOF'
    
    def error(self, message):
        """Raise a parsing error"""
        token = self.peek()
        raise SyntaxError(f"[Line {token.line}] {message}")

# Test function
def test_parser():
    """Test the parser with sample code"""
    from lexer import Lexer
    
    code = '''
    name is "Alice"
    age = 20 + 5
    say name
    say age
    '''
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    for node in ast:
        print(node)

if __name__ == "__main__":
    test_parser()