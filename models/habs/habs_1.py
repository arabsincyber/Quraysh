"""
Habs-1 — هبس (Trigram + Sampling)
====================================

نموذج Trigram — تعليمي.
يتدرب على جزء عمّ.

⚠️  تنبيه:
هذا النموذج **تعليمي فقط**.
"""

import random
from collections import defaultdict


def load_corpus(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def build_vocab(lines):
    words = set()
    for line in lines:
        for w in line.split():
            words.add(w)
    vocab = sorted(words)
    return vocab, {w: i for i, w in enumerate(vocab)}, {i: w for i, w in enumerate(vocab)}


class Habs1:
    """نموذج Trigram + Sampling"""

    def __init__(self):
        self.trigrams = defaultdict(lambda: defaultdict(int))
        self.bigrams = defaultdict(lambda: defaultdict(int))

    def train(self, lines):
        for line in lines:
            words = line.split()
            for i in range(len(words) - 1):
                self.bigrams[words[i]][words[i+1]] += 1
            for i in range(len(words) - 2):
                key = (words[i], words[i+1])
                self.trigrams[key][words[i+2]] += 1

    def _sample(self, candidates, temperature=1.0, top_k=3):
        """يختار كلمة — بشكل عشوائي مرجّح"""
        if not candidates:
            return None, 0

        items = list(candidates.items())
        # ترتيب
        items.sort(key=lambda x: x[1], reverse=True)
        # Top-K
        items = items[:top_k]

        # تحويل للاحتمالات
        total = sum(c for _, c in items)
        probs = [c / total for _, c in items]

        # Temperature
        if temperature != 1.0:
            probs = [p ** (1 / temperature) for p in probs]
            total = sum(probs)
            probs = [p / total for p in probs]

        # اختيار
        r = random.random()
        cum = 0
        for i, p in enumerate(probs):
            cum += p
            if r <= cum:
                return items[i][0], probs[i]

        return items[0][0], probs[0]

    def predict(self, w1, w2=None, temperature=1.0):
        """يتنبأ — مع Sampling"""
        if w2:
            key = (w1, w2)
            if key in self.trigrams and self.trigrams[key]:
                return self._sample(self.trigrams[key], temperature)

        if w1 in self.bigrams and self.bigrams[w1]:
            return self._sample(self.bigrams[w1], temperature)

        return None, 0

    def generate(self, start, length=6, temperature=0.8):
        """يولّد جملة — بدون تكرار"""
        words = start.split()
        used = set(words)

        for _ in range(length):
            if len(words) >= 2:
                candidates = dict(self.trigrams.get((words[-2], words[-1]), {}))
            elif len(words) == 1:
                candidates = dict(self.bigrams.get(words[-1], {}))
            else:
                break

            # استبعد الكلمات المستخدمة
            for w in list(candidates.keys()):
                if w in used:
                    del candidates[w]

            if not candidates:
                # لو ما فيه — نختار من كل
                if len(words) >= 2:
                    candidates = dict(self.trigrams.get((words[-2], words[-1]), {}))
                elif len(words) == 1:
                    candidates = dict(self.bigrams.get(words[-1], {}))

            next_w, _ = self._sample(candidates, temperature)
            if not next_w:
                break

            words.append(next_w)
            used.add(next_w)

        return " ".join(words)


def main():
    print("═" * 60)
    print("  🧠 هبس-1 — Habs-1 (Trigram + Sampling)")
    print("═" * 60)
    print()

    # البيانات
    path = "data/corpus.txt"
    lines = load_corpus(path)

    print(f"📖 البيانات:")
    print(f"   الأسطر: {len(lines)}")
    print(f"   الكلمات: {sum(len(l.split()) for l in lines)}")
    print()

    # القاموس
    vocab, word2id, id2word = build_vocab(lines)
    print(f"📚 القاموس: {len(vocab)} كلمة")
    print()

    # التدريب
    model = Habs1()
    print("🎓 جاري التدريب...")
    model.train(lines)
    print(f"   ✓ Bigrams: {len(model.bigrams)}")
    print(f"   ✓ Trigrams: {len(model.trigrams)}")
    print()

    # التوليد
    print("─" * 60)
    print("🎨 التوليد — 10 جمل:")
    print("─" * 60)
    print()

    starts = ["قل هو", "عم", "إنا", "يوم", "الله", "الذي"]

    for _ in range(3):  # 3 مرات
        for s in starts:
            result = model.generate(s, length=5, temperature=0.8)
            print(f"   [{s}] → {result}")
        print()

    print("═" * 60)
    print("  ⚠️  تعليمي فقط — احترام القرآن.")
    print("═" * 60)


if __name__ == "__main__":
    main()
