"""
Attention — آلية الانتباه
============================

Attention = "العقل" في Transformer.

يجيب على السؤال:
"عند معالجة كلمة، كم نركز على الكلمات الأخرى؟"

المعادلة:
Attention(Q, K, V) = softmax(Q × K^T / √d) × V

حيث:
- Q = Query (السؤال)
- K = Key (المفتاح)
- V = Value (القيمة)
- d = البعد
"""

import math


def dot_product(a, b):
    """الضرب الداخلي بين متجهين"""
    return sum(x * y for x, y in zip(a, b))


def softmax(values):
    """Softmax للأرقام"""
    exps = [math.exp(v) for v in values]
    total = sum(exps)
    return [e / total for e in exps]


def matmul(A, B):
    """ضرب مصفوفتين"""
    rows_A = len(A)
    cols_A = len(A[0])
    cols_B = len(B[0])

    result = [[0] * cols_B for _ in range(rows_A)]

    for i in range(rows_A):
        for j in range(cols_B):
            result[i][j] = sum(A[i][k] * B[k][j] for k in range(cols_A))

    return result


def transpose(M):
    """تبديل المصفوفة"""
    return [list(row) for row in zip(*M)]


def scale(matrix, factor):
    """ضرب مصفوفة بعامل"""
    return [[x * factor for x in row] for row in matrix]


def attention(Q, K, V, mask=None):
    """
    يحسب Attention.

    Args:
        Q: مصفوفة Query (n × d)
        K: مصفوفة Key (m × d)
        V: مصفوفة Value (m × d_v)
        mask: اختياري — قناع لإخفاء مواضع

    Returns:
        مصفوفة النواتج (n × d_v)
    """
    d = len(Q[0])

    # 1. Q × K^T
    K_T = transpose(K)
    scores = matmul(Q, K_T)

    # 2. القسمة على √d
    scores = scale(scores, 1.0 / math.sqrt(d))

    # 3. تطبيق Mask (إذا موجود)
    if mask:
        for i in range(len(scores)):
            for j in range(len(scores[i])):
                if mask[i][j] == 0:
                    scores[i][j] = -1e9  # قيمة صغيرة جداً

    # 4. Softmax على كل صف
    weights = [softmax(row) for row in scores]

    # 5. الضرب في V
    output = matmul(weights, V)

    return output, weights


def explain_attention():
    """يشرح Attention بمثال عملي"""

    print("═" * 65)
    print("  Attention — آلية الانتباه")
    print("═" * 65)
    print()

    # ═══ مثال: جملة بسيطة ═══
    # "السلام عليكم" — 3 كلمات

    print("📝 الجملة: 'السلام عليكم'")
    print()

    # متجهات وهمية (بُعد 4)
    # في الواقع: هذه نواتج Embedding

    Q = [
        [1.0, 0.0, 0.5, 0.3],  # "السلام" (Query)
        [0.5, 1.0, 0.3, 0.2],  # "عليكم" (Query)
    ]

    K = [
        [1.0, 0.0, 0.5, 0.3],  # "السلام" (Key)
        [0.5, 1.0, 0.3, 0.2],  # "عليكم" (Key)
        [0.3, 0.2, 1.0, 0.5],  # "أهلاً" (Key)
    ]

    V = [
        [1.0, 0.5, 0.3, 0.2],  # "السلام" (Value)
        [0.5, 1.0, 0.2, 0.3],  # "عليكم" (Value)
        [0.2, 0.3, 0.5, 1.0],  # "أهلاً" (Value)
    ]

    print("Query (Q) — السؤال:")
    for i, q in enumerate(Q):
        print(f"  Q[{i}]: {q}")
    print()

    print("Key (K) — المفتاح:")
    for i, k in enumerate(K):
        print(f"  K[{i}]: {k}")
    print()

    print("Value (V) — القيمة:")
    for i, v in enumerate(V):
        print(f"  V[{i}]: {v}")
    print()

    # ═══ الحساب ═══
    print("─" * 65)
    print("الحساب:")
    print("─" * 65)
    print()

    output, weights = attention(Q, K, V)

    print("1️⃣ Q × K^T (الضرب الداخلي):")
    K_T = transpose(K)
    scores = matmul(Q, K_T)
    for i, row in enumerate(scores):
        print(f"  صف {i}: {[f'{x:.3f}' for x in row]}")
    print()

    print("2️⃣ القسمة على √d (d=4 → √d=2):")
    scores_scaled = scale(scores, 1.0 / math.sqrt(4))
    for i, row in enumerate(scores_scaled):
        print(f"  صف {i}: {[f'{x:.3f}' for x in row]}")
    print()

    print("3️⃣ Softmax (تحويل لاحتمالات):")
    for i, row in enumerate(weights):
        print(f"  صف {i}: {[f'{x:.3f}' for x in row]}")
    print()

    print("📊 تفسير:")
    print(f"  Query[0] — يركز على:")
    for j, w in enumerate(weights[0]):
        bar = "█" * int(w * 30)
        print(f"    Key[{j}]: {w*100:5.1f}%  {bar}")
    print()

    print(f"  Query[1] — يركز على:")
    for j, w in enumerate(weights[1]):
        bar = "█" * int(w * 30)
        print(f"    Key[{j}]: {w*100:5.1f}%  {bar}")
    print()

    print("4️⃣ الناتج (weights × V):")
    for i, row in enumerate(output):
        print(f"  Output[{i}]: {[f'{x:.3f}' for x in row]}")
    print()

    print("═" * 65)
    print("  💡 الخلاصة:")
    print("═" * 65)
    print()
    print("  Attention يجيب على: 'كم أركز على كل كلمة؟'")
    print()
    print("  في المثال:")
    print("    - Query[0] ('السلام') ركّز على Key[0] ('السلام')")
    print("    - Query[1] ('عليكم') ركّز على Key[1] ('عليكم')")
    print()
    print("  هذا يعني: كل كلمة 'تنتبه' للكلمات المهمة لها.")
    print()


def simple_mask_example():
    """مثال على Mask — إخفاء الكلمات المستقبلية"""

    print("═" * 65)
    print("  Mask — إخفاء المستقبل")
    print("═" * 65)
    print()

    # 3 كلمات
    n = 3

    # Mask: كل كلمة تشوف الحاضر والماضي فقط
    mask = [
        [1, 0, 0],  # كلمة 0: تشوف فقط 0
        [1, 1, 0],  # كلمة 1: تشوف 0, 1
        [1, 1, 1],  # كلمة 2: تشوف 0, 1, 2
    ]

    print("Mask (المستقبل مخفي):")
    for row in mask:
        print(f"  {row}")
    print()

    print("💡 السبب:")
    print("  عند التنبؤ بالكلمة التالية، ما نبي النموذج يشوف المستقبل!")
    print()
    print("  K[0] → مسموح")
    print("  K[1] → مسموح فقط بعد K[0]")
    print("  K[2] → مسموح فقط بعد K[1]")
    print()


if __name__ == "__main__":
    explain_attention()
    simple_mask_example()
