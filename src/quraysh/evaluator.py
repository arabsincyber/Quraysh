"""
Evaluator — المُقيِّم
=====================

يقيّم شجرة التعبيرات وينتج النتيجة النهائية.
"""

from .lexer import tokenize
from .parser import parse_all, Expression
from .environment import build_default_env, Environment


class Quraysh:
    """مفسّر لسان قريش — الواجهة الرئيسية."""

    def __init__(self, env: Environment = None):
        self.env = env or build_default_env()

    def eval(self, expr: Expression):
        """يقيّم تعبير واحد."""
        # الأرقام والنصوص
        if isinstance(expr, (int, float, bool)):
            return expr

        # الرموز (أسماء المتغيرات والدوال)
        if isinstance(expr, str):
            if expr in self.env.vars:
                return self.env.vars[expr]
            return expr

        # القوائم (استدعاء دوال)
        if isinstance(expr, list):
            if not expr:
                return []

            # عمليات خاصة
            head = expr[0]

            # (قُلها x) => إرجاع x بدون تقييم
            if head == 'قُلها':
                if len(expr) < 2:
                    return None
                if isinstance(expr[1], str) and expr[1] in self.env.vars:
                    return self.env.vars[expr[1]]
                return expr[1]

            # (إنْ شرط صح خطأ)
            if head == 'إنْ':
                if len(expr) != 4:
                    raise ValueError("إنْ تحتاج 3 معاملات: (إنْ شرط صح خطأ)")
                شرط = self.eval(expr[1])
                if شرط:
                    return self.eval(expr[2])
                else:
                    return self.eval(expr[3])

            # استدعاء دالة عادي
            func = self.eval(head)
            args = [self.eval(arg) for arg in expr[1:]]

            if not callable(func):
                raise TypeError(f"ليس دالة: {head}")

            return func(*args)

        raise TypeError(f"نوع غير مدعوم: {type(expr)}")

    def eval_string(self, code: str):
        """يقيّم نص كامل — قد يحتوي عدة تعبيرات."""
        expressions = parse_all(code)
        result = None
        for expr in expressions:
            result = self.eval(expr)
        return result

    def eval_file(self, path: str):
        """يقيّم ملف."""
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        return self.eval_string(code)


# اختصار
def evaluate(code: str, env: Environment = None):
    """دالة سريعة للتقييم."""
    return Quraysh(env).eval_string(code)


if __name__ == "__main__":
    q = Quraysh()

    tests = [
        "(+ 5 3)",
        "(ألّم 1 2 3 4 5)",
        "(جَلَد 4 5)",
        "(جذر 16)",
        "(إنْ (أعظم 5 3) 100 200)",
        '(اطبع "السلام عليكم")',
    ]

    for code in tests:
        try:
            result = q.eval_string(code)
            print(f"{code:45} => {result}")
        except Exception as e:
            print(f"{code:45} => خطأ: {e}")
