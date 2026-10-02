"""
Evaluator — المُقيِّم
=====================

يقيّم شجرة التعبيرات وينتج النتيجة النهائية.

يدعم:
- العمليات الأساسية
- تعريف (define)
- لامدا (lambda)
- ماكرو (macro)
- إنْ / إذا (if-else)
- قيّم (eval) — تقييم ديناميكي
"""

from .lexer import tokenize
from .parser import parse_all, Expression
from .environment import build_default_env, Environment
from .crypto import دوال_التشفير
from .sql import دوال_القاعدة
from .networks import دوال_الشبكة


# ============================================================
#  Lambda & Macro
# ============================================================

class Lambda:
    """دالة لامبدا"""

    def __init__(self, params, body, env, interpreter):
        self.params = params
        self.body = body
        self.env = env
        self.interpreter = interpreter

    def __call__(self, *args):
        new_env = Environment(parent=self.env)
        for param, value in zip(self.params, args):
            new_env.set(param, value)

        body = self.body
        if isinstance(body, list) and len(body) > 1 and isinstance(body[0], list):
            # قائمة من التعبيرات (جسم متعدد)
            result = None
            for expr in body:
                result = self.interpreter.eval(expr, new_env)
            return result
        return self.interpreter.eval(body, new_env)

    def __repr__(self):
        return f"<لامدا ({' '.join(self.params)})>"


class Macro:
    """ماكرو"""

    def __init__(self, params, body, env, interpreter):
        self.params = params
        self.body = body
        self.env = env
        self.interpreter = interpreter

    def expand(self, args):
        new_env = Environment(parent=self.env)
        for param, value in zip(self.params, args):
            new_env.set(param, value)

        if isinstance(self.body, list) and len(self.body) > 1 and isinstance(self.body[0], list):
            result = None
            for expr in self.body:
                result = self.interpreter.eval(expr, new_env)
            return result
        return self.interpreter.eval(self.body, new_env)

    def __repr__(self):
        return f"<ماكرو ({' '.join(self.params)})>"


# ============================================================
#  المُقيِّم
# ============================================================

class Quraysh:
    """مفسّر لسان قريش."""

    def __init__(self, env: Environment = None):
        self.env = env or build_default_env()
        # دمج دوال التشفير في البيئة
        self.env.update(دوال_التشفير) if hasattr(self.env, 'update') else [self.env.set(k, v) for k, v in دوال_التشفير.items()]
        self.env.update(دوال_الشبكة) if hasattr(self.env, 'update') else [self.env.set(k, v) for k, v in دوال_الشبكة.items()]
        self.env.update(دوال_القاعدة) if hasattr(self.env, 'update') else [self.env.set(k, v) for k, v in دوال_القاعدة.items()]

    def eval(self, expr: Expression, env: Environment = None):
        """يقيّم تعبير واحد."""
        if env is None:
            env = self.env

        # 1. الأرقام والمنطقية
        if isinstance(expr, (int, float, bool)):
            return expr

        # 2. الرموز
        if isinstance(expr, str):
            try:
                return env.get(expr)
            except NameError:
                return expr

        # 3. القوائم
        if isinstance(expr, list):
            if not expr:
                return []

            head = expr[0]

            # ═══ الصيغ الخاصة ═══

            # (قُلها x)
            if head in ('قُلها', 'quote', 'اقتبس'):
                return expr[1] if len(expr) > 1 else None

            # (قيّم x) — تقييم ديناميكي
            if head in ('قيّم', 'قيم', 'eval'):
                if len(expr) != 2:
                    raise ValueError("قيّم: (قيّم تعبير)")
                # نقيّم المعامل أولاً — ثم نقيّم الناتج
                expanded = self.eval(expr[1], env)
                return self.eval(expanded, env)

            # (طبّق دالة args)
            if head in ('طبّق', 'apply'):
                if len(expr) < 3:
                    raise ValueError("طبّق: (طبّق دالة قائمة)")
                func = self.eval(expr[1], env)
                args = self.eval(expr[2], env)
                return func(*args)

            # (تعريف اسم قيمة)
            if head in ('تعريف', 'عرّف', 'define'):
                if len(expr) != 3:
                    raise ValueError("تعريف: (تعريف اسم قيمة)")
                name = expr[1]
                value = self.eval(expr[2], env)
                env.set(name, value)
                return None

            # (لامدا (معاملات) جسم)
            if head in ('لامدا', 'lambda'):
                if len(expr) < 3:
                    raise ValueError("لامدا: (لامدا (معاملات) جسم)")
                params = expr[1] if isinstance(expr[1], list) else [expr[1]]
                params = [p if isinstance(p, str) else str(p) for p in params]
                body = expr[2:]
                return Lambda(params, body if len(body) > 1 else body[0], env, self)

            # (ماكرو اسم (معاملات) جسم)
            if head in ('ماكرو', 'macro'):
                if len(expr) < 4:
                    raise ValueError("ماكرو: (ماكرو اسم (معاملات) جسم)")
                name = expr[1]
                params = expr[2] if isinstance(expr[2], list) else [expr[2]]
                params = [p if isinstance(p, str) else str(p) for p in params]
                body = expr[3:]
                macro = Macro(params, body if len(body) > 1 else body[0], env, self)
                env.set_macro(name, macro)
                return None

            # (إنْ شرط صح خطأ)
            if head == 'إنْ':
                if len(expr) != 4:
                    raise ValueError("إنْ: (إنْ شرط صح خطأ)")
                شرط = self.eval(expr[1], env)
                if شرط:
                    return self.eval(expr[2], env)
                return self.eval(expr[3], env)

            # (إذا شرط صح خطأ) / (إذا شرط صح)
            if head == 'إذا':
                if len(expr) == 4:
                    شرط = self.eval(expr[1], env)
                    return self.eval(expr[2] if شرط else expr[3], env)
                elif len(expr) == 3:
                    شرط = self.eval(expr[1], env)
                    return self.eval(expr[2], env) if شرط else None
                raise ValueError("إذا: (إذا شرط صح) أو (إذا شرط صح خطأ)")

            # ═══ الماكروز ═══

            if isinstance(head, str):
                macro = env.get_macro(head)
                if macro:
                    expanded = macro.expand(expr[1:])
                    return self.eval(expanded, env)

            # ═══ استدعاء دالة عادي ═══

            func = self.eval(head, env)
            args = [self.eval(arg, env) for arg in expr[1:]]

            if not callable(func):
                return func

            return func(*args)

        raise TypeError(f"نوع غير مدعوم: {type(expr)}")

    def eval_string(self, code: str):
        """يقيّم نص كامل."""
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


# ============================================================
#  دالة سريعة
# ============================================================

def evaluate(code: str, env: Environment = None):
    """دالة سريعة للتقييم."""
    return Quraysh(env).eval_string(code)


# ============================================================
#  اختبار
# ============================================================

if __name__ == "__main__":
    q = Quraysh()

    tests = [
        "(+ 5 3)",
        "(قيّم '(+ 1 2))",
        "(قيّم '(* 3 4))",
        "(قيّم '(ألّم 10 20 30))",
        "(تعريف س 10)",
        "س",
        "(قيّم 'س)",
        "(تعريف مربع (لامدا (ن) (* ن ن)))",
        "(مربع 5)",
        "(قيّم '(مربع 7))",
        "(طبّق + '(1 2 3))",
    ]

    for code in tests:
        try:
            result = q.eval_string(code)
            print(f"✓ {code:35} => {result}")
        except Exception as e:
            print(f"✗ {code:35} => خطأ: {e}")
