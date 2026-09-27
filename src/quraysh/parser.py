"""
Parser — المحلل النحوي
======================

يحوّل قائمة الرموز إلى شجرة تعبيرات (AST).
"""

from typing import List, Union
from .lexer import tokenize

Expression = Union[int, float, str, list]


class ParserError(Exception):
    """خطأ في التحليل النحوي"""
    pass


def atom(token: str) -> Expression:
    """يحوّل الرمز إلى قيمة (رقم، نص، أو رمز)."""
    try:
        return int(token)
    except ValueError:
        pass

    try:
        return float(token)
    except ValueError:
        pass

    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        return token[1:-1]

    return token


def parse(tokens: List[str]) -> Expression:
    """يحوّل قائمة الرموز إلى شجرة تعبير."""
    if not tokens:
        raise ParserError("قائمة الرموز فارغة")

    token = tokens.pop(0)

    if token == "(":
        lst = []
        while tokens and tokens[0] != ")":
            lst.append(parse(tokens))
        if not tokens:
            raise ParserError("قوس مغلق مفقود: )")
        tokens.pop(0)
        return lst

    elif token == ")":
        raise ParserError("قوس مغلق غير متوقع: )")

    return atom(token)


def parse_all(text: str) -> List[Expression]:
    """يحلّل نص كامل (عدة تعبيرات)."""
    tokens = tokenize(text)
    expressions = []

    while tokens:
        expressions.append(parse(tokens))

    return expressions


if __name__ == "__main__":
    from .lexer import tokenize

    tests = [
        "(+ 5 3)",
        '(اطبع "السلام عليكم")',
        "(ألّم ٥ ٣)",
        "(+ 1 2) (* 3 4)",
    ]

    for test in tests:
        try:
            print(f"Input : {test}")
            result = parse_all(test)
            print(f"Parsed: {result}")
            print()
        except ParserError as e:
            print(f"Error : {e}")
            print()
