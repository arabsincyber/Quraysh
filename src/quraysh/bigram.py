"""
bigram.py — نموذج لغوي عربي بسيط
====================================
مبني على نصوص فصيحة (القرآن الكريم).

- توقّع الكلمة التالية
- تصحيح الأخطاء الإملائية البرمجية
- خفيف جداً في الذاكرة
"""

import json
import re
from pathlib import Path
from collections import Counter, defaultdict


class نموذج_بيغرام:
    """نموذج Bigram مبني على corpus عربي"""

    def __init__(self):
        self.ثنائيات = defaultdict(Counter)
        self.مفردات = Counter()
        self.حجم = 0

    @staticmethod
    def _جرّد_التشكيل(نص):
        """يحذف التشكيل العربي"""
        تشكيل = "\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0655\u0670\u06D6\u06DC\u06DF\u06E0\u06E2\u06E3\u06E5\u06E6\u06E7\u06E8\u06EA\u06EB\u06EC\u06ED\u0640"
        return "".join(c for c in نص if c not in تشكيل)

    def تعلّم_نص(self, نص):
        """يعلّم من نص — يجرد التشكيل تلقائياً"""
        كلمات = [self._جرّد_التشكيل(ك) for ك in نص.split() if self._جرّد_التشكيل(ك)]
        for i in range(len(كلمات) - 1):
            self.ثنائيات[كلمات[i]][كلمات[i+1]] += 1
        for ك in كلمات:
            self.مفردات[ك] += 1
        self.حجم += len(كلمات)

    def تعلّم_ملف(self, مسار):
        with open(مسار, 'r', encoding='utf-8') as f:
            self.تعلّم_نص(f.read())

    def احتمالية(self, ك1, ك2):
        if ك1 not in self.ثنائيات:
            return 0.0
        مجموع = sum(self.ثنائيات[ك1].values())
        return self.ثنائيات[ك1][ك2] / مجموع if مجموع else 0.0

    def توقّع(self, كلمة, عدد=5):
        if كلمة not in self.ثنائيات:
            return []
        return self.ثنائيات[كلمة].most_common(عدد)

    def صحّح(self, كلمة, نطاق=3, حد_التكرار=3):
        """تصحيح يعتمد على Levenshtein + التكرار (يتجاهل التشكيل)"""
        # 1. الكلمة موجودة بكثرة → لا تصحيح
        if كلمة in self.مفردات and self.مفردات[كلمة] >= حد_التكرار:
            return كلمة

        # 2. جرّد التشكيل من الكلمة
        كلمة_مجردة = self._جرّد_التشكيل(كلمة)

        # 3. ابحث عن أقرب الكلمات
        مرشحات = []
        for مرشح, عدد in self.مفردات.most_common(5000):
            مرشح_مجرد = self._جرّد_التشكيل(مرشح)
            if abs(len(مرشح_مجرد) - len(كلمة_مجردة)) > نطاق:
                continue
            مسافة = self._levenshtein(كلمة_مجردة, مرشح_مجرد)
            if 0 < مسافة <= نطاق:
                مرشحات.append((مرشح, عدد, مسافة))

        if not مرشحات:
            return كلمة

        # 4. رتّب: الأقرب مسافة، الأعلى تكرار
        مرشحات.sort(key=lambda x: (x[2], -x[1]))
        return مرشحات[0][0]

    def صحّح_جملة(self, جملة, نطاق=2):
        return " ".join(self.صحّح(ك, نطاق) for ك in جملة.split())

    @staticmethod
    def _levenshtein(أ, ب):
        if len(أ) < len(ب):
            return نموذج_بيغرام._levenshtein(ب, أ)
        if len(ب) == 0:
            return len(أ)
        سابق = list(range(len(ب) + 1))
        for i, c1 in enumerate(أ):
            حالي = [i + 1]
            for j, c2 in enumerate(ب):
                إدخال = سابق[j + 1] + 1
                حذف = حالي[j] + 1
                استبدال = سابق[j] + (c1 != c2)
                حالي.append(min(إدخال, حذف, استبدال))
            سابق = حالي
        return سابق[-1]

    def حفظ(self, مسار):
        data = {
            "ثنائيات": {k: dict(v) for k, v in self.ثنائيات.items()},
            "مفردات": dict(self.مفردات),
            "حجم": self.حجم,
        }
        with open(مسار, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
        حجم = Path(مسار).stat().st_size
        print(f"💾 حُفظ: {مسار} ({حجم // 1024} KB)")

    @classmethod
    def حمّل(cls, مسار):
        with open(مسار, 'r', encoding='utf-8') as f:
            data = json.load(f)
        ن = cls()
        ن.ثنائيات = defaultdict(Counter,
            {k: Counter(v) for k, v in data["ثنائيات"].items()})
        ن.مفردات = Counter(data["مفردات"])
        ن.حجم = data.get("حجم", 0)
        return ن

    def إحصاءات(self):
        return {
            "كلمات_كلية": self.حجم,
            "كلمات_فريدة": len(self.مفردات),
            "ثنائيات": len(self.ثنائيات),
        }

    def __repr__(self):
        return f"<بيغرام: {self.حجم:,} كلمة، {len(self.مفردات):,} فريدة>"


# ═══════════════════════════════════════════════════════════
#  دوال للربط بالمفسّر
# ═══════════════════════════════════════════════════════════

_نموذج_عام = None


def _احصل_على_النموذج():
    global _نموذج_عام
    if _نموذج_عام is None:
        مسار = Path(__file__).parent.parent.parent / "models/corpus/bigram/quran_bigram.json"
        if مسار.exists():
            _نموذج_عام = نموذج_بيغرام.حمّل(str(مسار))
        else:
            _نموذج_عام = نموذج_بيغرام()
    return _نموذج_عام


def توقّع_الكلمة(كلمة, عدد=5):
    return _احصل_على_النموذج().توقّع(كلمة, عدد)


def صحّح_كلمة(كلمة):
    return _احصل_على_النموذج().صحّح(كلمة)


def صحّح_جملة(جملة):
    return _احصل_على_النموذج().صحّح_جملة(جملة)


دوال_البيغرام = {
    "توقّع_الكلمة": توقّع_الكلمة,
    "صحّح_كلمة": صحّح_كلمة,
    "صحّح_جملة": صحّح_جملة,
}


# ═══════════════════════════════════════════════════════════
#  تجربة سريعة
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    مسار = "models/corpus/quran/quran.txt"
    if not Path(مسار).exists():
        print(f"⚠️ الملف غير موجود: {مسار}")
        sys.exit(1)

    print("🧠 تدريب النموذج على القرآن...")
    نموذج = نموذج_بيغرام()
    نموذج.تعلّم_ملف(مسار)

    print(f"✅ {نموذج}")
    print()
    for k, v in نموذج.إحصاءات().items():
        print(f"  • {k}: {v:,}")
    print()

    print("🔮 توقّع:")
    for كلمة in ["بسم", "الحمد", "الله", "الرحمن"]:
        توقعات = نموذج.توقّع(كلمة, 3)
        print(f"  بعد '{كلمة}': {توقعات}")
    print()

    print("🔧 تصحيح:")
    for كلمة in ["الرحم", "الحم", "الله", "بسم"]:
        مصحح = نموذج.صحّح(كلمة)
        رمز = "✓" if مصحح == كلمة else "→"
        print(f"  '{كلمة}' {رمز} '{مصحح}'")

    print()
    print("💾 حفظ النموذج...")
    نموذج.حفظ("models/corpus/bigram/quran_bigram.json")
