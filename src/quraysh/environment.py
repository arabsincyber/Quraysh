"""
Environment — البيئة والدوال
=============================

تحتوي على جميع الدوال المدمجة في لسان قريش.

الأقسام:
- الحساب
- المقارنات
- عمليات مكارثي
- الرياضيات الأساسية
- FORTRAN (الحسابات العلمية)
- معالجة النصوص
- قوائم متقدمة
- أدوات
"""

import math
from typing import Any, Dict

# استيراد FORTRAN
try:
    from .fortran import (
        جيب, جيب_تمام, ظل, ظل_تمام, قاطع, قاطع_تمام,
        جيب_عكسي, جيب_تمام_عكسي, ظل_عكسي,
        لوغاريتم, لوغاريتم_طبيعي, أس,
        جذر_ن, قوة_ن,
        مساحة_مثلث, مساحة_دائرة, محيط_دائرة,
        مساحة_مستطيل, مساحة_مربع,
        حجم_كرة, حجم_مكعب,
        متوسط, وسيط, انحراف, مجموع, أكبر, أصغر,
        باي, هـ,
    )
    FORTRAN_AVAILABLE = True
except ImportError:
    FORTRAN_AVAILABLE = False
    print("⚠️  تحذير: مكتبة FORTRAN غير متوفرة")


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


# ═══════════════════════════════════════════════════════════
#  الحساب
# ═══════════════════════════════════════════════════════════

def ألّم(*args): return sum(args)
def انقص(a, b): return a - b
def جَلَد(*args):
    r = 1
    for x in args: r *= x
    return r
def قَسَم(a, b): return a / b
def بَقِي(a, b): return a % b


# ═══════════════════════════════════════════════════════════
#  المقارنات
# ═══════════════════════════════════════════════════════════

def أعظم(a, b): return a > b
def أدنى(a, b): return a < b
def نظير(a, b): return a == b


# ═══════════════════════════════════════════════════════════
#  عمليات مكارثي
# ═══════════════════════════════════════════════════════════

def أوّل(ق): return ق[0]
def بَقِيَّة(ق): return ق[1:] if len(ق) > 1 else []
def ضُمَّ(ع, ق): return [ع] + ق
def واحِد(ش): return not isinstance(ش, list)


# ═══════════════════════════════════════════════════════════
#  الرياضيات الأساسية
# ═══════════════════════════════════════════════════════════

def جذر(ن): return math.sqrt(ن)
def مطلق(ن): return abs(ن)
def قوة(أ, ب): return أ ** ب
def زوجي(ن): return ن % 2 == 0
def فردي(ن): return ن % 2 != 0


# ═══════════════════════════════════════════════════════════
#  معالجة النصوص
# ═══════════════════════════════════════════════════════════

def طول(نص): return len(نص)
def انشقاق(نص, فاصل=" "): return نص.split(فاصل)
def دمج(*args): return "".join(str(a) for a in args)
def جزء(نص, بداية, نهاية=None):
    if نهاية is None: return نص[بداية:]
    return نص[بداية:نهاية]
def يحتوي(نص, بحث): return بحث in نص
def استبدال(نص, قديم, جديد): return نص.replace(قديم, جديد)
def كبير(نص): return نص.upper()
def صغير(نص): return نص.lower()
def شذّب(نص): return نص.strip()
def نص(ش): return str(ش)
def رقم(نص_أو_رقم):
    try: return int(نص_أو_رقم)
    except (ValueError, TypeError):
        try: return float(نص_أو_رقم)
        except (ValueError, TypeError):
            raise ValueError(f"ليس رقماً: {نص_أو_رقم}")


# ═══════════════════════════════════════════════════════════
#  قوائم متقدمة
# ═══════════════════════════════════════════════════════════

def قائمة(*args): return list(args)
def أضف(ق, عنصر): return ق + [عنصر]
def عنصر(ق, فهرس): return ق[فهرس]
def مدى(بداية, نهاية): return list(range(بداية, نهاية))


# ═══════════════════════════════════════════════════════════
#  أدوات
# ═══════════════════════════════════════════════════════════

def إنْ(شرط, صح, خطأ): return صح if شرط else خطأ
def اطبع(*args):
    print(*args)
    return None
def اقتبس(x): return x


# ═══════════════════════════════════════════════════════════
#  بناء البيئة الافتراضية
# ═══════════════════════════════════════════════════════════

def build_default_env() -> Environment:
    """ينشئ البيئة الافتراضية بكل الدوال المدمجة."""
    env = Environment()

    # الحساب
    env.vars['ألّم'] = ألّم
    env.vars['انقص'] = انقص
    env.vars['جَلَد'] = جَلَد
    env.vars['قَسَم'] = قَسَم
    env.vars['بَقِي'] = بَقِي
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

    # الرياضيات الأساسية
    env.vars['جذر'] = جذر
    env.vars['مطلق'] = مطلق
    env.vars['قوة'] = قوة
    env.vars['زوجي'] = زوجي
    env.vars['فردي'] = فردي

    # ═══ FORTRAN — الحسابات العلمية ═══
    if FORTRAN_AVAILABLE:
        env.vars['جيب'] = جيب
        env.vars['جيب_تمام'] = جيب_تمام
        env.vars['ظل'] = ظل
        env.vars['ظل_تمام'] = ظل_تمام
        env.vars['قاطع'] = قاطع
        env.vars['قاطع_تمام'] = قاطع_تمام
        env.vars['جيب_عكسي'] = جيب_عكسي
        env.vars['جيب_تمام_عكسي'] = جيب_تمام_عكسي
        env.vars['ظل_عكسي'] = ظل_عكسي
        env.vars['لوغاريتم'] = لوغاريتم
        env.vars['لوغاريتم_طبيعي'] = لوغاريتم_طبيعي
        env.vars['أس'] = أس
        env.vars['جذر_ن'] = جذر_ن
        env.vars['قوة_ن'] = قوة_ن
        env.vars['مساحة_مثلث'] = مساحة_مثلث
        env.vars['مساحة_دائرة'] = مساحة_دائرة
        env.vars['محيط_دائرة'] = محيط_دائرة
        env.vars['مساحة_مستطيل'] = مساحة_مستطيل
        env.vars['مساحة_مربع'] = مساحة_مربع
        env.vars['حجم_كرة'] = حجم_كرة
        env.vars['حجم_مكعب'] = حجم_مكعب
        env.vars['متوسط'] = متوسط
        env.vars['وسيط'] = وسيط
        env.vars['انحراف'] = انحراف
        env.vars['مجموع'] = مجموع
        env.vars['أكبر'] = أكبر
        env.vars['أصغر'] = أصغر
        env.vars['باي'] = باي
        env.vars['هـ'] = هـ

    # معالجة النصوص
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

    # قوائم
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
    print(f"عدد الدوال: {len(env.vars)}")
    print()
    if FORTRAN_AVAILABLE:
        print("FORTRAN:")
        print(f"  جيب(0) = {جيب(0)}")
        print(f"  مساحة_مثلث(10, 6) = {مساحة_مثلث(10, 6)}")
        print(f"  متوسط(90, 80) = {متوسط(90, 80)}")
