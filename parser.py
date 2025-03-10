from typing import Union

# Define JSON types
JsonValue = Union[dict, list, str, int, float, bool, None]

# JSON Token Types
class TokenType:
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    NULL = "NULL"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    COMMA = ","
    COLON = ":"
    EOF = "EOF"

# Token class
class Token:
    def __init__(self, type: str, value: Union[str, int, float, bool, None]):
        self.type = type
        self.value = value

# Scanner (Tokenizes JSON)
class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.current = 0

    def scan_tokens(self):
        """Scans JSON input and returns a list of tokens."""
        tokens = []
        while not self.is_at_end():
            char = self.advance()
            if char in " \t\n\r":
                continue  # Skip whitespace
            elif char in "{}[],:":
                tokens.append(Token(char, char))  # Punctuation tokens
            elif char == '"':
                tokens.append(self.scan_string())
            elif char.isdigit() or char == "-":
                tokens.append(self.scan_number(char))
            elif char.isalpha():
                tokens.append(self.scan_keyword(char))
            else:
                raise ValueError(f"Unexpected character: {char}")
        tokens.append(Token(TokenType.EOF, None))
        return tokens

    def advance(self) -> str:
        """Consumes and returns the next character."""
        char = self.source[self.current]
        self.current += 1
        return char

    def peek(self) -> str:
        """Returns the next character without consuming it."""
        return self.source[self.current] if not self.is_at_end() else ""

    def is_at_end(self) -> bool:
        """Checks if we've reached the end of input."""
        return self.current >= len(self.source)

    def scan_string(self) -> Token:
        """Scans a string token."""
        start = self.current
        while self.peek() != '"' and not self.is_at_end():
            self.advance()
        if self.is_at_end():
            raise ValueError("Unterminated string")
        self.advance()  # Consume closing quote
        return Token(TokenType.STRING, self.source[start:self.current - 1])

    def scan_number(self, first_char: str) -> Token:
        """Scans a number token."""
        number = first_char
        while self.peek().isdigit() or self.peek() == ".":
            number += self.advance()
        return Token(TokenType.NUMBER, float(number) if "." in number else int(number))

    def scan_keyword(self, first_char: str) -> Token:
        """Scans keywords: true, false, null."""
        word = first_char
        while self.peek().isalpha():
            word += self.advance()
        if word == "true":
            return Token(TokenType.BOOLEAN, True)
        elif word == "false":
            return Token(TokenType.BOOLEAN, False)
        elif word == "null":
            return Token(TokenType.NULL, None)
        raise ValueError(f"Unexpected keyword: {word}")

# Parser (Converts Tokens into Python Objects)
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> JsonValue:
        """Parses the JSON tokens into a Python object."""
        return self.parse_value()

    def parse_value(self) -> JsonValue:
        """Determines what type of JSON value is being parsed."""
        token = self.advance()
        if token.type in (TokenType.STRING, TokenType.NUMBER, TokenType.BOOLEAN, TokenType.NULL):
            return token.value
        elif token.type == TokenType.LEFT_BRACE:
            return self.parse_object()
        elif token.type == TokenType.LEFT_BRACKET:
            return self.parse_array()
        raise ValueError(f"Unexpected token: {token.type}")

    def parse_object(self) -> dict:
        """Parses a JSON object (dictionary)."""
        obj = {}
        while self.peek().type != TokenType.RIGHT_BRACE:
            key = self.expect(TokenType.STRING, "Expected string key")
            self.expect(TokenType.COLON, "Expected ':' after key")
            obj[key.value] = self.parse_value()
            if self.peek().type == TokenType.COMMA:
                self.advance()
            else:
                break
        self.expect(TokenType.RIGHT_BRACE, "Expected '}' at end of object")
        return obj

    def parse_array(self) -> list:
        """Parses a JSON array (list)."""
        arr = []
        while self.peek().type != TokenType.RIGHT_BRACKET:
            arr.append(self.parse_value())
            if self.peek().type == TokenType.COMMA:
                self.advance()
            else:
                break
        self.expect(TokenType.RIGHT_BRACKET, "Expected ']' at end of array")
        return arr

    def advance(self) -> Token:
        """Moves to the next token and returns it."""
        token = self.tokens[self.current]
        self.current += 1
        return token

    def peek(self) -> Token:
        """Returns the current token without consuming it."""
        return self.tokens[self.current]

    def expect(self, token_type: str, error_message: str) -> Token:
        """Checks the next token type and consumes it if valid."""
        if self.peek().type != token_type:
            raise ValueError(error_message)
        return self.advance()

# Function to parse JSON
def parse_json(json_str: str) -> JsonValue:
    """Main function to parse JSON from a string."""
    scanner = Scanner(json_str)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    return parser.parse()

# Example usage
if __name__ == "__main__":
    json_text = '''
    {
        "name": "Alice",
        "age": 25,
        "isStudent": false,
        "grades": [90, 85, 88],
        "address": {"city": "New York", "zip": "10001"}
    }
    '''
    result = parse_json(json_text)
    print(result)
