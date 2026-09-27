"""
Quraysh — لسان قريش
==================

لغة برمجة عربية كاملة، مبنية على مبادئ Lisp (1958).
"""

__version__ = "2.0.0"
__author__ = "Mohammed"
__license__ = "MIT"

# مؤقتاً — حتى نكمل باقي الملفات
from .lexer import tokenize, تعريب_الأرقام
# from .parser import parse, parse_all
# from .environment import build_default_env, Environment
# from .evaluator import evaluate, Quraysh

__all__ = [
    "tokenize",
    "تعريب_الأرقام",
    "__version__",
]
