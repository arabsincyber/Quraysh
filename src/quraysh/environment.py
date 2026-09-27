"""
Environment — البيئة والدوال
=============================

تحتوي على جميع الدوال المدمجة في لسان قريش.

الأقسام:
- الحساب
- المقارنات
- عمليات مكارثي
- رياضيات
- معالجة النصوص
- قوائم متقدمة
- أدوات
"""

import math
from typing import Any, Dict


class Environment:
    """بيئة التنفيذ — تحتوي على المتغيرات والدوال."""

    def __init__(self, parent=None):
        self.vars: Dict[str, Any] = {}
        self.parent = parent
        self.macros: Dict[str, Any] = {}

    def get(self, name: str):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"متغير غير معروف: {name}")

    def set(self, name: str, value):
        self.vars[name] = value
        return value

    def get_macro(self, name: str):
        if name in self.macros:
            return self.macros[name]
        if self.parent:
            return self.parent.get_macro(name)
        return None

    def set_macro(self, name: str, func):
        self.macros[name] = func


# ============================================================
#  الحساب
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


# ============================================================
#  المقارنات
# ============================================================

def أعظم(a, b): return a > b
def أدنى(a, b): return a < b
def نظير(a, b): return a == b


# ============================================================
#  عمليات مكارثي
# ============================================================

def أوّل(ق): return ق[0]
def بَقِيَّة(ق): return ق[1:] if len(ق) > 1 else []
def ضُمَّ(ع, ق): return [ع] + ق
def واحِد(ش): return not isinstance(ش, list)


# ============================================================
#  الرياضيات
# ============================================================

def جذر(ن): return math.sqrt(ن)
def مطلق(ن): return abs(ن)
def قوة(أ, ب): return أ ** ب
def زوجي(ن): return ن % 2 == 0
def فردي(ن): return ن % 2 != 0


# ============================================================
#  معالجة النصوص (جديد)
# ============================================================

def طول(نص):
    """طول النص أو القائمة"""
    return len(نص)


def انشقاق(نص, فاصل=" "):
    """تقسيم النص إلى قائمة"""
    return نص.split(فاصل)


def دمج(*args):
    """دمج نصوص"""
    return "".join(str(a) for a in args)


def جزء(نص, بداية, نهاية=None):
    """جزء من النص"""
    if نهاية is None:
        return نص[بداية:]
    return نص[بداية:نهاية]


def يحتوي(نص, بحث):
    """هل النص يحتوي على؟"""
    return بحث in نص


def استبدال(نص, قديم, جديد):
    """استبدال نص"""
    return نص.replace(قديم, جديد)


def كبير(نص):
    """تحويل لحروف كبيرة"""
    return نص.upper()


def صغير(نص):
    """تحويل لحروف صغيرة"""
    return نص.lower()


def شذّب(نص):
    """إزالة المسافات الزائدة"""
    return نص.strip()


def نص(ش):
    """تحويل أي شي إلى نص"""
    return str(ش)


def رقم(نص_أو_رقم):
    """تحويل نص إلى رقم"""
    try:
        return int(نص_أو_رقم)
    except (ValueError, TypeError):
        try:
            return float(نص_أو_رقم)
        except (ValueError, TypeError):
            raise ValueError(f"ليس رقماً: {نص_أو_رقم}")


# ============================================================
#  قوائم متقدمة
# ============================================================

def قائمة(*args):
    """إنشاء قائمة"""
    return list(args)


def أضف(ق, عنصر):
    """إضافة عنصر لقائمة"""
    return ق + [عنصر]


def عنصر(ق, فهرس):
    """جلب عنصر من قائمة"""
    return ق[فهرس]


def مدى(بداية, نهاية):
    """إنشاء قائمة أرقام من بداية إلى نهاية"""
    return list(range(بداية, نهاية))


# ============================================================
#  أدوات
# ============================================================

def إنْ(شرط, صح, خطأ):
    return صح if شرط else خطأ


def اطبع(*args):
    print(*args)
    return None


def اقتبس(x):
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

    # ═══ معالجة النصوص (جديد) ═══
    env.vars['طول'] = طول
    env.vars['انشقاق'] = انشقاق
    env.vars['دمج'] = دمج
    env.vars['جزء'] = جزء
    env.vars['يحتوي'] = يحتوي
    env.vars['استبدال'] = استبدال
    env.vars['كبير'] = كبير
    env.vars['صغير'] = صغير
    env.vars['شذّب'] = شذّب
    env.vars['نص'] = نص
    env.vars['رقم'] = رقم

    # ═══ قوائم متقدمة (جديد) ═══
    env.vars['قائمة'] = قائمة
    env.vars['list'] = قائمة
    env.vars['أضف'] = أضف
    env.vars['عنصر'] = عنصر
    env.vars['مدى'] = مدى

    # أدوات
    env.vars['إنْ'] = إنْ
    env.vars['اطبع'] = اطبع
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

    # اختبار معالجة النصوص
    print("اختبار معالجة النصوص:")
    print("  (طول \"السلام\")             =>", طول("السلام"))
    print("  (انشقاق \"أ ب ج\" \" \")      =>", انشقاق("أ ب ج", " "))
    print("  (دمج \"أ\" \"ب\" \"ج\")        =>", دمج("أ", "ب", "ج"))
    print("  (جزء \"السلام\" 0 3)         =>", جزء("السلام", 0, 3))
    print("  (يحتوي \"السلام\" \"س\")      =>", يحتوي("السلام", "س"))
    print("  (استبدال \"أب\" \"أ\" \"ب\")   =>", استبدال("أب", "أ", "ب"))
    print("  (كبير \"abc\")               =>", كبير("abc"))
    print("  (صغير \"ABC\")               =>", صغير("ABC"))
    print()
    print("اختبار القوائم:")
    print("  (قائمة 1 2 3)              =>", قائمة(1, 2, 3))
    print("  (أضف (قائمة 1 2) 3)        =>", أضف([1, 2], 3))
    print("  (مدى 1 5)                  =>", مدى(1, 5))
