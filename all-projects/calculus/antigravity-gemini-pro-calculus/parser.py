import re
from math_ast import (
    Node, ConstNode, VarNode, AddNode, SubNode,
    MulNode, DivNode, PowNode, SinNode, CosNode
)

class ParseError(Exception):
    pass

def tokenize(text: str):
    token_specification = [
        ('NUMBER',   r'\d+(\.\d*)?'),  # Integer or decimal number
        ('FUNC',     r'sin|cos'),      # Functions
        ('VAR',      r'[a-zA-Z_]\w*'), # Identifiers (variables)
        ('OP',       r'[+\-*/^()]'),   # Operators
        ('SKIP',     r'[ \t]+'),       # Skip over spaces and tabs
        ('MISMATCH', r'.'),            # Any other character
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    for mo in re.finditer(tok_regex, text):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise ParseError(f'Unexpected character {value!r}')
        yield kind, value

class Parser:
    def __init__(self, text: str):
        self.tokens = list(tokenize(text))
        self.pos = 0

    def parse(self) -> Node:
        if not self.tokens:
            raise ParseError("Empty expression")
        node = self.expr()
        if self.pos < len(self.tokens):
            raise ParseError(f"Unexpected token at end: {self.tokens[self.pos]}")
        return node

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None, None

    def match(self, expected_kind, expected_value=None):
        kind, value = self.peek()
        if kind == expected_kind and (expected_value is None or value == expected_value):
            self.pos += 1
            return value
        return None

    def expect(self, expected_kind, expected_value=None):
        value = self.match(expected_kind, expected_value)
        if value is None:
            kind, val = self.peek()
            raise ParseError(f"Expected {expected_kind}{'('+expected_value+')' if expected_value else ''}, got {kind}('{val}')")
        return value

    def expr(self) -> Node:
        node = self.term()
        while True:
            op = self.match('OP', '+') or self.match('OP', '-')
            if op:
                right = self.term()
                if op == '+':
                    node = AddNode(node, right)
                else:
                    node = SubNode(node, right)
            else:
                break
        return node

    def term(self) -> Node:
        node = self.factor()
        while True:
            op = self.match('OP', '*') or self.match('OP', '/')
            if op:
                right = self.factor()
                if op == '*':
                    node = MulNode(node, right)
                else:
                    node = DivNode(node, right)
            else:
                break
        return node

    def factor(self) -> Node:
        node = self.base()
        while True:
            op = self.match('OP', '^')
            if op:
                right = self.factor() # ^ is right-associative usually, so we call factor()
                node = PowNode(node, right)
            else:
                break
        return node

    def base(self) -> Node:
        # Check for unary minus
        if self.match('OP', '-'):
            return MulNode(ConstNode(-1), self.base())

        if self.match('OP', '('):
            node = self.expr()
            self.expect('OP', ')')
            return node

        func = self.match('FUNC')
        if func:
            self.expect('OP', '(')
            inner = self.expr()
            self.expect('OP', ')')
            if func == 'sin':
                return SinNode(inner)
            elif func == 'cos':
                return CosNode(inner)

        num = self.match('NUMBER')
        if num:
            return ConstNode(float(num))

        var = self.match('VAR')
        if var:
            return VarNode(var)

        kind, value = self.peek()
        raise ParseError(f"Expected number, variable, function, or '(', got {value!r}")

def parse_expr(text: str) -> Node:
    parser = Parser(text)
    return parser.parse()
