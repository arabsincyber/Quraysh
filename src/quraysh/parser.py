"""
Parser — المحلل النحوي
======================

يحوّل الرموز إلى شجرة تعبيرات.

يدعم:
- الأقواس
- الاقتباس ('x) — يتحول إلى (قُلها x)
"""

from typing import List, Union
from .lexer import tokenize

Expression = Union[int, float, str, list]


class ParserError(Exception):
    pass


def atom(token: str) -> Expression:
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
    if not tokens:
        raise ParserError("قائمة الرموز فارغة")

    token = tokens.pop(0)

    # قوس فتح
    if token == "(":
        lst = []
        while tokens and tokens[0] != ")":
            lst.append(parse(tokens))
        if not tokens:
            raise ParserError("قوس مغلق مفقود: )")
        tokens.pop(0)
        return lst

    # قوس إغلاق
    elif token == ")":
        raise ParserError("قوس مغلق غير متوقع: )")

    # اقتباس 'x → (قُلها x)
    elif token == "'":
        if not tokens:
            raise ParserError("اقتباس بدون تعبير: '")
        quoted = parse(tokens)
        return ['قُلها', quoted]

    return atom(token)


def parse_all(text: str) -> List[Expression]:
    tokens = tokenize(text)
    expressions = []
    while tokens:
        expressions.append(parse(tokens))
    return expressions


if __name__ == "__main__":
    tests = [
        "(+ 5 3)",
        "(قيّم '(+ 1 2))",
        "(قيّم 'س)",
        "(قيّم '(مربع 7))",
        "(طبّق + '(1 2 3))",
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
