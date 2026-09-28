"""
Habs-0 — هبس
=============

نموذج Transformer مصغّر — تعليمي.
يتدرب على سورة الإخلاص.

⚠️  تنبيه:
هذا النموذج **تعليمي فقط**.
- ما يعطي تفسير
- ما يعطي فتوى
- ما يعطي معنى
- مجرد تجربة تقنية
"""

import random


# ═══════════════════════════════════════════════════════════
#  البيانات
# ═══════════════════════════════════════════════════════════

def load_corpus(path):
    """يقرأ النص من ملف"""
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines


def build_vocab(lines):
    """يبني قاموس الكلمات"""
    words = set()
    for line in lines:
        for w in line.split():
            words.add(w)

    vocab = sorted(words)
    word2id = {w: i for i, w in enumerate(vocab)}
    id2word = {i: w for i, w in enumerate(vocab)}

    return vocab, word2id, id2word


# ═══════════════════════════════════════════════════════════
#  النموذج
# ═══════════════════════════════════════════════════════════

def softmax(x):
    m = max(x)
    exps = [pow(2.718281828, v - m) for v in x]
    s = sum(exps)
    return [e / s for e in exps]


class Habs0:
    """نموذج بسيط — Bigram"""

    def __init__(self, vocab_size):
        self.vocab_size = vocab_size
        # مصفوفة الأوزان: [عدد الكلمات] × [عدد الكلمات]
        # القيمة = احتمال الانتقال
        self.W = [[0.0] * vocab_size for _ in range(vocab_size)]

    def train(self, lines, word2id):
        """التدريب — عدّ الانتقالات"""
        for line in lines:
            ids = [word2id[w] for w in line.split()]
            for i in range(len(ids) - 1):
                self.W[ids[i]][ids[i + 1]] += 1.0

        # تحويل لاحتمالات (softmax لكل صف)
        for i in range(self.vocab_size):
            if sum(self.W[i]) > 0:
                self.W[i] = softmax(self.W[i])

    def predict(self, word, word2id, id2word):
        """يتنبأ بالكلمة التالية"""
        if word not in word2id:
            return None

        i = word2id[word]
        probs = self.W[i]

        # أعلى احتمال
        best_j = max(range(len(probs)), key=lambda j: probs[j])
        return id2word[best_j], probs[best_j]


# ═══════════════════════════════════════════════════════════
#  التشغيل
# ═══════════════════════════════════════════════════════════

def main():
    print("═" * 60)
    print("  🧠 هبس-0 — Habs-0")
    print("  نموذج تعليمي — سورة الإخلاص")
    print("═" * 60)
    print()

    # 1. قراءة البيانات
    path = "data/corpus.txt"
    lines = load_corpus(path)

    print(f"📖 البيانات ({len(lines)} أسطر):")
    for line in lines:
        print(f"   {line}")
    print()

    # 2. بناء القاموس
    vocab, word2id, id2word = build_vocab(lines)

    print(f"📚 القاموس ({len(vocab)} كلمة):")
    print(f"   {vocab}")
    print()

    # 3. النموذج
    model = Habs0(len(vocab))
    print("🎓 جاري التدريب...")
    model.train(lines, word2id)
    print("   ✓ تم التدريب")
    print()

    # 4. الاختبار
    print("─" * 60)
    print("🎯 الاختبار — التنبؤ بالكلمة التالية:")
    print("─" * 60)
    print()

    tests = ["قل", "هو", "الله", "الصمد"]

    for word in tests:
        result = model.predict(word, word2id, id2word)
        if result:
            next_word, prob = result
            print(f"   {word} → {next_word}  ({prob*100:.1f}%)")
        else:
            print(f"   {word} → (غير موجود)")

    print()
    print("═" * 60)
    print("  ⚠️  تنبيه:")
    print("═" * 60)
    print()
    print("  هذا النموذج **تعليمي فقط**.")
    print("  - ما يعطي تفسير")
    print("  - ما يعطي فتوى")
    print("  - ما يعطي معنى")
    print("  - مجرد تجربة تقنية")
    print()
    print("  القرآن — كتاب الله.")
    print("  نحترمه — ولا نتلاعب به.")
    print()


if __name__ == "__main__":
    main()
