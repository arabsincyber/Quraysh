"""
Lexer — المحلل اللفظي
=====================

يحوّل النص العربي إلى قائمة رموز (tokens).
"""

import re
from typing import List

خريطة_الأرقام = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def تعريب_الأرقام(text: str) -> str:
    """تحوّل الأرقام العربية إلى إنجليزية."""
    return text.translate(خريطة_الأرقام)


نمط_الرمز = re.compile(
    r'"[^"]*"'
    r'|[()]'
    r"|[^\s()]+"
)


def tokenize(text: str) -> List[str]:
    """يحوّل النص إلى قائمة رموز."""
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
        "(ألّم ٥ ٣)",
        "(جَلَد 4 5) ; تعليق",
    ]

    for test in tests:
        print(f"Input : {test}")
        print(f"Tokens: {tokenize(test)}")
        print()
