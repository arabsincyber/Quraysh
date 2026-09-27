"""
Softmax — تحويل الأرقام إلى احتمالات
======================================

Softmax(x_i) = exp(x_i) / Σ exp(x_j)

هذا الملف يشرح Softmax خطوة بخطوة.
"""

import math


def softmax(logits, temperature=1.0):
    """
    يحوّل Logits إلى احتمالات.

    Args:
        logits: قائمة أرقام خام
        temperature: معامل التحكم في الإبداع (افتراضي: 1.0)

    Returns:
        قائمة احتمالات (تجمع لـ 1.0)
    """
    # 1. قسمة على Temperature
    scaled = [x / temperature for x in logits]

    # 2. الأس
    exps = [math.exp(x) for x in scaled]

    # 3. المجموع
    total = sum(exps)

    # 4. القسمة
    return [e / total for e in exps]


def explain_softmax(logits, temperature=1.0):
    """يشرح Softmax خطوة بخطوة"""
    print("=" * 60)
    print(f"Softmax — شرح خطوة بخطوة")
    print("=" * 60)
    print()
    print(f"Logits: {logits}")
    print(f"Temperature: {temperature}")
    print()

    # 1. القسمة على Temperature
    print("الخطوة 1: القسمة على Temperature")
    scaled = [x / temperature for x in logits]
    for i, (x, s) in enumerate(zip(logits, scaled)):
        print(f"  logit[{i}]: {x} / {temperature} = {s:.4f}")
    print()

    # 2. الأس
    print("الخطوة 2: حساب الأس (exp)")
    exps = [math.exp(x) for x in scaled]
    for i, e in enumerate(exps):
        print(f"  exp({scaled[i]:.4f}) = {e:.4f}")
    print()

    # 3. المجموع
    print("الخطوة 3: حساب المجموع")
    total = sum(exps)
    print(f"  المجموع: {total:.4f}")
    print()

    # 4. القسمة
    print("الخطوة 4: القسمة (للحصول على الاحتمالات)")
    probs = [e / total for e in exps]
    for i, p in enumerate(probs):
        print(f"  احتمال[{i}]: {exps[i]:.4f} / {total:.4f} = {p:.4f} ({p*100:.2f}%)")
    print()

    # التحقق
    print("التحقق:")
    print(f"  مجموع الاحتمالات: {sum(probs):.4f}")
    print(f"  ✓ = 1.0" if abs(sum(probs) - 1.0) < 0.0001 else "  ✗")
    print()


def main():
    """أمثلة توضيحية"""

    # القاموس (المفردات)
    vocab = ["السلام", "عليكم", "مرحبا", "أهلاً"]

    # Logits من نموذج وهمي
    logits = [2.5, 1.2, 0.3, -0.5]

    print(f"المفردات: {vocab}")
    print(f"Logits: {logits}")
    print()

    # ═══ مثال 1: Softmax عادي ═══
    print("═" * 60)
    print("مثال 1: Softmax عادي (T=1.0)")
    print("═" * 60)
    print()

    probs = softmax(logits)

    for word, prob in zip(vocab, probs):
        bar = "█" * int(prob * 50)
        print(f"  {word:10} {prob*100:6.2f}%  {bar}")

    print()

    # ═══ مثال 2: Temperature منخفضة (T=0.5) ═══
    print("═" * 60)
    print("مثال 2: Temperature منخفضة (T=0.5) — حاد")
    print("═" * 60)
    print()

    probs = softmax(logits, temperature=0.5)

    for word, prob in zip(vocab, probs):
        bar = "█" * int(prob * 50)
        print(f"  {word:10} {prob*100:6.2f}%  {bar}")

    print()

    # ═══ مثال 3: Temperature عالية (T=2.0) ═══
    print("═" * 60)
    print("مثال 3: Temperature عالية (T=2.0) — مبدع")
    print("═" * 60)
    print()

    probs = softmax(logits, temperature=2.0)

    for word, prob in zip(vocab, probs):
        bar = "█" * int(prob * 50)
        print(f"  {word:10} {prob*100:6.2f}%  {bar}")

    print()

    # ═══ شرح مفصّل ═══
    print("═" * 60)
    print("شرح مفصّل لـ Softmax (T=1.0)")
    print("═" * 60)
    print()

    explain_softmax(logits, temperature=1.0)


if __name__ == "__main__":
    main()
