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
- BASIC (التعليمية)
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

# استيراد BASIC
try:
    from .basic import (
        اقرأ, اقرأ_رقم, اقرأ_عدد,
        كرر_من_إلى, كرر_خطوة,
        طول_نص, جزء_نص, يسار, يمين,
        رمز, حرف, عشوائي,
        تقريب_عدد, صحيح, مطلق_عدد, إشارة,
    )
    BASIC_AVAILABLE = True
except ImportError:
    BASIC_AVAILABLE = False


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

    # الرياضيات
    env.vars['جذر'] = جذر
    env.vars['مطلق'] = مطلق
    env.vars['قوة'] = قوة
    env.vars['زوجي'] = زوجي
    env.vars['فردي'] = فردي

    # ═══ FORTRAN ═══
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

    # ═══ BASIC ═══
    if BASIC_AVAILABLE:
        env.vars['اقرأ'] = اقرأ
        env.vars['اقرأ_رقم'] = اقرأ_رقم
        env.vars['اقرأ_عدد'] = اقرأ_عدد
        env.vars['كرر_من_إلى'] = كرر_من_إلى
        env.vars['كرر_خطوة'] = كرر_خطوة
        env.vars['طول_نص'] = طول_نص
        env.vars['جزء_نص'] = جزء_نص
        env.vars['يسار'] = يسار
        env.vars['يمين'] = يمين
        env.vars['رمز'] = رمز
        env.vars['حرف'] = حرف
        env.vars['عشوائي'] = عشوائي
        env.vars['تقريب_عدد'] = تقريب_عدد
        env.vars['صحيح'] = صحيح
        env.vars['مطلق_عدد'] = مطلق_عدد
        env.vars['إشارة'] = إشارة

    # معالجة النصوص
    env.vars['طول'] = len
    env.vars['انشقاق'] = lambda نص, فاصل=" ": نص.split(فاصل)
    env.vars['دمج'] = lambda *args: "".join(str(a) for a in args)
    env.vars['جزء'] = lambda نص, بداية, نهاية=None: نص[بداية:] if نهاية is None else نص[بداية:نهاية]
    env.vars['يحتوي'] = lambda نص, بحث: بحث in نص
    env.vars['استبدال'] = lambda نص, قديم, جديد: نص.replace(قديم, جديد)
    env.vars['كبير'] = lambda نص: نص.upper()
    env.vars['صغير'] = lambda نص: نص.lower()
    env.vars['شذّب'] = lambda نص: نص.strip()
    env.vars['نص'] = str
    env.vars['رقم'] = lambda x: int(x) if str(x).isdigit() else float(x)

    # قوائم
    env.vars['قائمة'] = lambda *args: list(args)
    env.vars['list'] = lambda *args: list(args)
    env.vars['أضف'] = lambda ق, عنصر: ق + [عنصر]
    env.vars['عنصر'] = lambda ق, فهرس: ق[فهرس]
    env.vars['مدى'] = lambda بداية, نهاية: list(range(بداية, نهاية))

    # أدوات
    env.vars['إنْ'] = إنْ
    env.vars['اطبع'] = اطبع
    env.vars['اقتبس'] = اقتبس
    env.vars['quote'] = اقتبس

    # ثوابت
    env.vars['أجل'] = True
    env.vars['كلا'] = False


    # ═══ Networks ═══
    if NETWORKS_AVAILABLE:
        env.vars['اتصل_بـ'] = اتصل_بـ
        env.vars['أرسل_بيانات'] = أرسل_بيانات
        env.vars['حمّل'] = حمّل
        env.vars['بينغ'] = بينغ
        env.vars['استعلم_dns'] = استعلم_dns
        env.vars['افتح_منفذ'] = افتح_منفذ
        env.vars['ip_الحالي'] = ip_الحالي

    return env



if __name__ == "__main__":
    env = build_default_env()
    print(f"عدد الدوال: {len(env.vars)}")
    print()
    print(f"FORTRAN: {'✅' if FORTRAN_AVAILABLE else '❌'}")
    print(f"BASIC:   {'✅' if BASIC_AVAILABLE else '❌'}")

# ═══════════════════════════════════════════════════════════
#  Networks — إضافة جديدة
# ═══════════════════════════════════════════════════════════

try:
    from .networks import (
        اتصل_بـ, أرسل_بيانات, حمّل, بينغ,
        استعلم_dns, افتح_منفذ, ip_الحالي,
    )
    NETWORKS_AVAILABLE = True
except ImportError:
    NETWORKS_AVAILABLE = False
