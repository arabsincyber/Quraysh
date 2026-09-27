"""
Sandbox — الصندوق الزجاجي
===========================

نظام المحاكاة في لسان قريش.

المبدأ: "لا تنفيذ بدون رؤية"

كل عملية تُحاكى أولاً، وتُعرض للمستخدم،
ثم يُطلب منه الموافقة قبل التنفيذ الفعلي.
"""

from typing import List, Dict, Any
from .lexer import tokenize
from .parser import parse_all


class Process:
    """عملية واحدة في البرنامج"""

    def __init__(self, نوع: str, تفاصيل: str):
        self.نوع = نوع  # قراءة، كتابة، حساب، طباعة، ...
        self.تفاصيل = تفاصيل

    def __repr__(self):
        return f"{self.نوع}: {self.تفاصيل}"

    def __str__(self):
        return f"   → {self.وصف()}"

    def وصف(self) -> str:
        """وصف مقروء للعملية"""
        رموز = {
            "طباعة": "📤 طباعة",
            "قراءة": "📥 قراءة",
            "حساب": "🧮 حساب",
            "تعريف": "📝 تعريف",
            "شرط": "🔀 شرط",
            "تكرار": "🔁 تكرار",
            "شبكة": "🌐 شبكة",
            "ملف": "📁 ملف",
        }
        return f"{رموز.get(self.نوع, self.نوع)} — {self.تفاصيل}"


class Sandbox:
    """المحاكي — يحلل الكود ويعرض العمليات"""

    def __init__(self):
        self.العمليات: List[Process] = []
        self.الأذونات_المستخدمة: set = set()

    def حلل(self, source: str) -> List[Process]:
        """يحلل الكود ويستخرج العمليات"""
        self.العمليات = []
        self.الأذونات_المستخدمة = set()

        try:
            expressions = parse_all(source)
        except Exception as e:
            # إذا فشل التحليل، نرجّع قائمة فاضية
            return self.العمليات

        for expr in expressions:
            self._حلل_تعبير(expr)

        return self.العمليات

    def _حلل_تعبير(self, expr):
        """يحلل تعبير واحد"""
        if not isinstance(expr, list) or not expr:
            return

        head = expr[0]

        # طباعة
        if head == "اطبع":
            self.العمليات.append(Process(
                "طباعة",
                f"طبع {len(expr) - 1} قيمة"
            ))

        # قراءة (مدخلات)
        elif head == "اقرأ":
            self.العمليات.append(Process(
                "قراءة",
                "قراءة من المستخدم"
            ))
            self.الأذونات_المستخدمة.add("مدخلات")

        # عمليات حسابية
        elif head in ("ألّم", "انقص", "جَلَد", "قَسَم", "+", "-", "*", "/", "بَقِي"):
            self.العمليات.append(Process(
                "حساب",
                f"عملية {head}"
            ))

        # تعريف
        elif head in ("تعريف", "عرّف"):
            self.العمليات.append(Process(
                "تعريف",
                f"تعريف {expr[1] if len(expr) > 1 else '؟'}"
            ))

        # شرط
        elif head in ("إنْ", "إذا"):
            self.العمليات.append(Process(
                "شرط",
                "تفرّع شرطي"
            ))
            # حلل الفروع
            for فرع in expr[2:]:
                self._حلل_تعبير(فرع)

        # تكرار
        elif head == "تكرار":
            self.العمليات.append(Process(
                "تكرار",
                "حلقة تكرار"
            ))
            # حلل الجسم
            for بند in expr[1:]:
                self._حلل_تعبير(بند)

        # عمليات حساسة
        elif head in ("شبكة", "اتصل"):
            self.العمليات.append(Process(
                "شبكة",
                "اتصال شبكي"
            ))
            self.الأذونات_المستخدمة.add("شبكة")

        elif head in ("اقرأ_ملف", "اكتب_ملف"):
            self.العمليات.append(Process(
                "ملف",
                f"عملية ملف: {head}"
            ))
            self.الأذونات_المستخدمة.add("قراءة_ملفات")

        else:
            # تعبير عادي — نستمر بالتحليل الداخلي
            for فرع in expr[1:]:
                if isinstance(فرع, list):
                    self._حلل_تعبير(فرع)


# ============================================================
#  عرض التقرير
# ============================================================

def عرض_المحاكاة(عمليات: List[Process], أذونات: set) -> str:
    """يعرض تقرير المحاكاة"""
    lines = [
        "",
        "🔍 مرحلة المحاكاة:",
        "─" * 44,
    ]

    if not عمليات:
        lines.append("   (لا توجد عمليات قابلة للتحليل)")
    else:
        for i, عملية in enumerate(عمليات, 1):
            lines.append(f"   {i}. {عملية.وصف()}")

    lines.append("")
    lines.append("📊 الأذونات المستخدمة:")
    if أذونات:
        for إذن in sorted(أذونات):
            lines.append(f"   ⚠️  {إذن}")
    else:
        lines.append("   ✓ لا أذونات حساسة")

    lines.append("─" * 44)

    return "\n".join(lines)


# ============================================================
#  اختبار
# ============================================================

if __name__ == "__main__":
    كود = """
    (اطبع "السلام عليكم")
    (اطبع (ألّم 10 20))
    (اطبع (جذر 144))
    """

    sb = Sandbox()
    عمليات = sb.حلل(كود)

    print("اختبار المحاكاة:")
    print()
    print(عرض_المحاكاة(عمليات, sb.الأذونات_المستخدمة))
