"""
Jusu++ Lexer - Converts source code to tokens
"""
import re

class Token:
    """A single token in the source code"""
    def __init__(self, type, value, line, column):
        self.type = type    # e.g., 'KEYWORD', 'IDENTIFIER', 'NUMBER'
        self.value = value  # e.g., 'say', 'myVar', '42'
        self.line = line    # line number in source
        self.column = column # column number
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line})"

class Lexer:
    """Converts Jusu++ source code into tokens"""
    
    # All keywords in Jusu++
    KEYWORDS = {
        'say', 'if', 'else', 'for', 'while',
        'function', 'return', 'is', 'to', 'in',
        'true', 'false', 'null', 'end'
    }
    
    def __init__(self, source_code):
        self.source = source_code
        self.position = 0   # Current position in source
        self.line = 1       # Current line number
        self.column = 1     # Current column number
        self.tokens = []    # List of tokens we find
    
    def tokenize(self):
        """Convert source code to list of tokens"""
        while self.position < len(self.source):
            char = self.source[self.position]
            
            # Skip whitespace (but track newlines)
            if char == ' ' or char == '\t':
                self.advance()
            elif char == '\n':
                self.add_token('NEWLINE', '\n')
                self.line += 1
                self.column = 1
                self.advance()
            # Skip comments
            elif char == '#':
                self.skip_comment()
            # Handle strings (single or double quoted)
            elif char in ('"', "'"):
                self.read_string()
            # Handle numbers
            elif char.isdigit():
                self.read_number()
            # Handle identifiers and keywords
            elif char.isalpha() or char == '_':
                self.read_identifier()
            # Handle operators
            elif char in '+-*/=<>!':
                self.read_operator()
            # Handle punctuation
            elif char in '():{},.[]:':
                self.add_token('PUNCTUATION', char)
                self.advance()
            else:
                # Unknown character
                raise SyntaxError(f"Unknown character '{char}' at line {self.line}")
        
        # Ensure source ends with a NEWLINE token so the parser can consume statement terminators
        if not self.tokens or self.tokens[-1].type != 'NEWLINE':
            self.add_token('NEWLINE', '\n')
        # Add EOF token
        self.add_token('EOF', '')
        return self.tokens
    
    def advance(self, n=1):
        """Move forward n characters"""
        self.position += n
        self.column += n
    
    def add_token(self, token_type, value):
        """Add a token to the list"""
        token = Token(token_type, value, self.line, self.column)
        self.tokens.append(token)
    
    def skip_comment(self):
        """Skip everything until end of line"""
        while self.position < len(self.source) and self.source[self.position] != '\n':
            self.advance()
    
    def read_string(self):
        """Read a string literal (supports single or double quotes and common escapes)"""
        quote = self.source[self.position]
        start_pos = self.position
        self.advance()  # Skip opening quote
        value_chars = []
        
        while self.position < len(self.source):
            ch = self.source[self.position]
            # Handle escapes
            if ch == '\\':
                self.advance()
                if self.position >= len(self.source):
                    raise SyntaxError("Unterminated string (escape at EOF)")
                esc = self.source[self.position]
                esc_map = {'n':'\n','t':'\t','r':'\r','\\':'\\','"':'"',"'":"'"}
                value_chars.append(esc_map.get(esc, esc))
                self.advance()
                continue
            # Closing quote
            if ch == quote:
                break
            value_chars.append(ch)
            self.advance()
        
        if self.position >= len(self.source):
            raise SyntaxError("Unterminated string")
        
        value = ''.join(value_chars)
        self.add_token('STRING', value)
        self.advance()  # Skip closing quote
    
    def read_number(self):
        """Read a number literal"""
        start_pos = self.position
        
        # Read integer part
        while self.position < len(self.source) and self.source[self.position].isdigit():
            self.advance()
        
        # Check for decimal point
        if self.position < len(self.source) and self.source[self.position] == '.':
            self.advance()  # Skip '.'
            # Read fractional part
            while self.position < len(self.source) and self.source[self.position].isdigit():
                self.advance()
        
        value = self.source[start_pos:self.position]
        self.add_token('NUMBER', value)
    
    def read_identifier(self):
        """Read an identifier or keyword"""
        start_pos = self.position
        
        # Read while we have letters, digits, or underscores
        while (self.position < len(self.source) and 
               (self.source[self.position].isalnum() or self.source[self.position] == '_')):
            self.advance()
        
        value = self.source[start_pos:self.position]
        
        # Check if it's a keyword
        if value in self.KEYWORDS:
            self.add_token('KEYWORD', value)
        else:
            self.add_token('IDENTIFIER', value)
    
    def read_operator(self):
        """Read an operator (could be 1 or 2 chars)"""
        char = self.source[self.position]
        
        # Check for 2-character operators
        if self.position + 1 < len(self.source):
            two_char = self.source[self.position:self.position + 2]
            if two_char in ('==', '!=', '<=', '>=', '+=', '-=', '*=', '/='):
                self.add_token('OPERATOR', two_char)
                self.advance(2)
                return
        
        # Single character operator
        self.add_token('OPERATOR', char)
        self.advance()

# Test function
def test_lexer():
    """Test the lexer with sample code"""
    code = '''
    name is "Alice"
    age = 25
    say name
    '''
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    for token in tokens:
        print(f"{token.type:12} '{token.value}'")

if __name__ == "__main__":
    test_lexer()