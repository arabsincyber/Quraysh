"""
Sampling — اختيار الكلمة التالية
===================================

يشرح:
- Greedy Sampling (اختيار الأعلى)
- Top-K Sampling
- Top-P (Nucleus) Sampling
- Random Sampling مع Temperature
"""

import math
import random


def softmax(logits, temperature=1.0):
    """يحوّل Logits إلى احتمالات."""
    scaled = [x / temperature for x in logits]
    exps = [math.exp(x) for x in scaled]
    total = sum(exps)
    return [e / total for e in exps]


def greedy_sample(logits):
    """يختار الكلمة الأعلى احتمالاً — دائماً."""
    return max(range(len(logits)), key=lambda i: logits[i])


def top_k_sample(logits, k=3, temperature=1.0):
    """Top-K Sampling — يختار من أفضل K فقط."""
    # 1. ترتيب حسب Logits (تنازلياً)
    indexed = list(enumerate(logits))
    indexed.sort(key=lambda x: x[1], reverse=True)

    # 2. اختيار أفضل K
    top_k = indexed[:k]

    # 3. استخراج Logits للـ top-K
    top_logits = [logit for _, logit in top_k]
    top_indices = [idx for idx, _ in top_k]

    # 4. Softmax
    probs = softmax(top_logits, temperature)

    # 5. اختيار عشوائي حسب الاحتمالات
    chosen = random.choices(range(len(probs)), weights=probs, k=1)[0]

    return top_indices[chosen]


def top_p_sample(logits, p=0.9, temperature=1.0):
    """Top-P (Nucleus) Sampling — يختار حتى الوصول لـ p."""
    # 1. ترتيب تنازلياً
    indexed = list(enumerate(logits))
    indexed.sort(key=lambda x: x[1], reverse=True)

    # 2. Softmax على الكل
    all_probs = softmax([logit for _, logit in indexed], temperature)

    # 3. التراكمي — نوقف عند p
    cumulative = 0.0
    selected = []
    for i, prob in enumerate(all_probs):
        selected.append(i)
        cumulative += prob
        if cumulative >= p:
            break

    # 4. استخراج الاحتمالات المختارة
    selected_probs = [all_probs[i] for i in selected]
    selected_indices = [indexed[i][0] for i in selected]

    # 5. إعادة التطبيع
    total = sum(selected_probs)
    normalized = [sp / total for sp in selected_probs]

    # 6. اختيار عشوائي
    chosen = random.choices(range(len(normalized)), weights=normalized, k=1)[0]

    return selected_indices[chosen]


def random_sample(logits, temperature=1.0):
    """Random Sampling — من كل المفردات."""
    probs = softmax(logits, temperature)
    return random.choices(range(len(probs)), weights=probs, k=1)[0]


# ═══════════════════════════════════════════════════════════
#  العرض
# ═══════════════════════════════════════════════════════════

def show_distribution(vocab, probs, title=""):
    """يعرض التوزيع بشكل مرئي"""
    print(f"  {title}")
    for word, prob in zip(vocab, probs):
        bar = "█" * int(prob * 40)
        print(f"    {word:10} {prob*100:5.1f}%  {bar}")
    print()


def main():
    """أمثلة توضيحية"""

    # المفردات
    vocab = ["السلام", "عليكم", "مرحبا", "أهلاً", "صباح", "مساء"]

    # Logits من نموذج وهمي
    logits = [2.5, 1.2, 0.3, -0.5, -1.0, -2.0]

    print("═" * 65)
    print("  Sampling — اختيار الكلمة التالية")
    print("═" * 65)
    print()

    print(f"المفردات: {vocab}")
    print(f"Logits: {logits}")
    print()

    # التوزيع الأصلي
    probs = softmax(logits)
    show_distribution(vocab, probs, "التوزيع الأصلي (Softmax):")

    # ═══ Greedy ═══
    print("═" * 65)
    print("  1️⃣ Greedy Sampling — دائماً الأعلى")
    print("═" * 65)
    print()

    chosen = greedy_sample(logits)
    print(f"  اختار: {vocab[chosen]}")
    print(f"  (دائماً نفس النتيجة — لا إبداع)")
    print()

    # ═══ Top-K ═══
    print("═" * 65)
    print("  2️⃣ Top-K Sampling (K=3)")
    print("═" * 65)
    print()

    print("  نأخذ أفضل 3 فقط:")
    indexed = sorted(enumerate(logits), key=lambda x: x[1], reverse=True)
    top_k_indices = [idx for idx, _ in indexed[:3]]
    print(f"  → {[vocab[i] for i in top_k_indices]}")
    print()

    print("  10 محاولات:")
    results = {}
    for _ in range(10):
        chosen = top_k_sample(logits, k=3)
        word = vocab[chosen]
        results[word] = results.get(word, 0) + 1

    for word, count in sorted(results.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"    {word:10} {count:2} / 10  {bar}")
    print()

    # ═══ Top-P ═══
    print("═" * 65)
    print("  3️⃣ Top-P (Nucleus) Sampling (P=0.9)")
    print("═" * 65)
    print()

    # أي كلمات داخلة
    indexed = sorted(enumerate(logits), key=lambda x: x[1], reverse=True)
    all_probs = softmax([logit for _, logit in indexed])
    cumulative = 0.0
    selected = []
    for i, prob in enumerate(all_probs):
        selected.append(i)
        cumulative += prob
        if cumulative >= 0.9:
            break

    print(f"  نأخذ حتى 90%:")
    print(f"  → {[vocab[indexed[i][0]] for i in selected]}")
    print()

    print("  10 محاولات:")
    results = {}
    for _ in range(10):
        chosen = top_p_sample(logits, p=0.9)
        word = vocab[chosen]
        results[word] = results.get(word, 0) + 1

    for word, count in sorted(results.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"    {word:10} {count:2} / 10  {bar}")
    print()

    # ═══ Random ═══
    print("═" * 65)
    print("  4️⃣ Random Sampling — من كل المفردات")
    print("═" * 65)
    print()

    print("  10 محاولات:")
    results = {}
    for _ in range(10):
        chosen = random_sample(logits)
        word = vocab[chosen]
        results[word] = results.get(word, 0) + 1

    for word, count in sorted(results.items(), key=lambda x: -x[1]):
        bar = "█" * count
        print(f"    {word:10} {count:2} / 10  {bar}")
    print()

    print("═" * 65)
    print("  الخلاصة:")
    print("═" * 65)
    print()
    print("  🎯 Greedy    → دقيق لكن ممل")
    print("  🎯 Top-K     → متوازن (يحذف الغريب)")
    print("  🎯 Top-P     → مرن (يتكيف مع التوزيع)")
    print("  🎯 Random    → مبدع لكن ممكن يخطئ")
    print()


if __name__ == "__main__":
    random.seed(42)  # لتكرار النتائج
    main()
