"""
Lexer — المحلل اللفظي
=====================

يحوّل النص العربي إلى قائمة رموز (tokens).

يدعم:
- الأرقام العربية
- النصوص
- الأقواس
- الاقتباس ('x)
"""

import re
from typing import List

خريطة_الأرقام = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def تعريب_الأرقام(text: str) -> str:
    return text.translate(خريطة_الأرقام)


# النمط:
# - نص بين " "
# - قوس ( أو )
# - اقتباس '
# - أي رمز آخر (بدون مسافة، بدون قوس، بدون اقتباس)
نمط_الرمز = re.compile(
    r'"[^"]*"'          # نص
    r'|[()]'            # قوس
    r"|'"               # اقتباس
    r"|[^\s()']+"       # رمز عادي
)


def tokenize(text: str) -> List[str]:
    text = تعريب_الأرقام(text)
    text = "\n".join(
        line.split(";")[0] if ";" in line else line
        for line in text.splitlines()
    )
    return نمط_الرمز.findall(text)


if __name__ == "__main__":
    tests = [
        "(+ 5 3)",
        '(اطبع "السلام عليكم")',
        "(قيّم '(+ 1 2))",
        "(قيّم 'س)",
        "(ألّم ٥ ٣)",
    ]

    for test in tests:
        print(f"Input : {test}")
        print(f"Tokens: {tokenize(test)}")
        print()
