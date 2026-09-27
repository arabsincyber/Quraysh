"""
Environment — البيئة والدوال
=============================

تحتوي على جميع الدوال المدمجة في لسان قريش.
"""

import math
from typing import Any, Dict


class Environment:
    """بيئة التنفيذ — تحتوي على المتغيرات والدوال."""

    def __init__(self, parent=None):
        self.vars: Dict[str, Any] = {}
        self.parent = parent
        self.macros: Dict[str, Any] = {}  # الماكروز

    def get(self, name: str):
        """جلب قيمة متغير."""
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"متغير غير معروف: {name}")

    def set(self, name: str, value):
        """تعيين قيمة متغير."""
        self.vars[name] = value
        return value

    def get_macro(self, name: str):
        """جلب ماكرو."""
        if name in self.macros:
            return self.macros[name]
        if self.parent:
            return self.parent.get_macro(name)
        return None

    def set_macro(self, name: str, func):
        """تعريف ماكرو."""
        self.macros[name] = func


# ============================================================
#  الدوال المدمجة
# ============================================================

def ألّم(*args): return sum(args)
def انقص(a, b): return a - b
def جَلَد(*args):
    r = 1
    for x in args:
        r *= x
    return r
def قَسَم(a, b): return a / b
def بَقِي(a, b): return a % b


def أعظم(a, b): return a > b
def أدنى(a, b): return a < b
def نظير(a, b): return a == b


def أوّل(ق): return ق[0]
def بَقِيَّة(ق): return ق[1:] if len(ق) > 1 else []
def ضُمَّ(ع, ق): return [ع] + ق
def واحِد(ش): return not isinstance(ش, list)


def جذر(ن): return math.sqrt(ن)
def مطلق(ن): return abs(ن)
def قوة(أ, ب): return أ ** ب
def زوجي(ن): return ن % 2 == 0
def فردي(ن): return ن % 2 != 0


def إنْ(شرط, صح, خطأ):
    return صح if شرط else خطأ


def اطبع(*args):
    print(*args)
    return None


def قائمة(*args):
    """إنشاء قائمة — مفيد للماكروز"""
    return list(args)


def اقتبس(x):
    """اقتباس — يمنع التقييم"""
    return x


# ============================================================
#  بناء البيئة الافتراضية
# ============================================================

def build_default_env() -> Environment:
    """ينشئ البيئة الافتراضية بكل الدوال المدمجة."""
    env = Environment()

    # الحساب
    env.vars['ألّم'] = ألّم
    env.vars['انقص'] = انقص
    env.vars['جَلَد'] = جَلَد
    env.vars['قَسَم'] = قَسَم
    env.vars['بَقِي'] = بَقِي

    # الرموز
    env.vars['+'] = ألّم
    env.vars['-'] = انقص
    env.vars['*'] = جَلَد
    env.vars['/'] = قَسَم
    env.vars['%'] = بَقِي

    # المقارنات
    env.vars['أعظم'] = أعظم
    env.vars['أدنى'] = أدنى
    env.vars['نظير'] = نظير
    env.vars['>'] = أعظم
    env.vars['<'] = أدنى
    env.vars['='] = نظير

    # مكارثي
    env.vars['أوّل'] = أوّل
    env.vars['بَقِيَّة'] = بَقِيَّة
    env.vars['ضُمَّ'] = ضُمَّ
    env.vars['واحِد'] = واحِد
    env.vars['قُلها'] = lambda x: x

    # رياضيات
    env.vars['جذر'] = جذر
    env.vars['مطلق'] = مطلق
    env.vars['قوة'] = قوة
    env.vars['زوجي'] = زوجي
    env.vars['فردي'] = فردي

    # شروط
    env.vars['إنْ'] = إنْ

    # طباعة
    env.vars['اطبع'] = اطبع

    # قوائم (للماكروز)
    env.vars['قائمة'] = قائمة
    env.vars['list'] = قائمة
    env.vars['اقتبس'] = اقتبس
    env.vars['quote'] = اقتبس

    # ثوابت
    env.vars['أجل'] = True
    env.vars['كلا'] = False

    return env


if __name__ == "__main__":
    env = build_default_env()
    print("عدد الدوال:", len(env.vars))
    print()
    print("أمثلة:")
    print("  (ألّم 1 2 3)  =>", env.get('ألّم')(1, 2, 3))
    print("  (جَلَد 4 5)   =>", env.get('جَلَد')(4, 5))
    print("  (قائمة 1 2 3) =>", env.get('قائمة')(1, 2, 3))
