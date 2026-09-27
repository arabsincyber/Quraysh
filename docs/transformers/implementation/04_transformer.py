"""
Transformer — النموذج الكامل (مصغّر)
======================================

يبني Transformer كامل:
- Embedding
- Positional Encoding
- Multi-Head Attention
- Feed Forward
- Layer Norm

هذا النموذج **تعليمي** — مو إنتاجي.
"""

import math
import random


# ═══════════════════════════════════════════════════════════
#  الأساسيات
# ═══════════════════════════════════════════════════════════

def softmax(values):
    exps = [math.exp(v - max(values)) for v in values]
    total = sum(exps)
    return [e / total for e in exps]


def matmul(A, B):
    cols_B = len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(len(B)))
             for j in range(cols_B)]
            for i in range(len(A))]


def transpose(M):
    return [list(row) for row in zip(*M)]


def scale(M, f):
    return [[x * f for x in row] for row in M]


def add(A, B):
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))]
            for i in range(len(A))]


# ═══════════════════════════════════════════════════════════
#  Embedding
# ═══════════════════════════════════════════════════════════

class Embedding:
    """يحوّل الكلمات إلى متجهات"""

    def __init__(self, vocab_size, d_model, seed=42):
        random.seed(seed)
        self.d_model = d_model
        self.vocab_size = vocab_size
        self.table = [
            [random.gauss(0, 0.1) for _ in range(d_model)]
            for _ in range(vocab_size)
        ]

    def __call__(self, token_id):
        return self.table[token_id]


# ═══════════════════════════════════════════════════════════
#  Positional Encoding
# ═══════════════════════════════════════════════════════════

def positional_encoding(seq_len, d_model):
    """
    يضيف معلومات الموضع.

    المعادلة:
    PE(pos, 2i)   = sin(pos / 10000^(2i/d))
    PE(pos, 2i+1) = cos(pos / 10000^(2i/d))
    """
    pe = [[0.0] * d_model for _ in range(seq_len)]

    for pos in range(seq_len):
        for i in range(d_model):
            if i % 2 == 0:
                pe[pos][i] = math.sin(pos / (10000 ** (i / d_model)))
            else:
                pe[pos][i] = math.cos(pos / (10000 ** ((i - 1) / d_model)))

    return pe


# ═══════════════════════════════════════════════════════════
#  Attention
# ═══════════════════════════════════════════════════════════

def scaled_dot_product_attention(Q, K, V, mask=None):
    """Attention الأساسي"""
    d_k = len(Q[0])

    scores = matmul(Q, transpose(K))
    scores = scale(scores, 1.0 / math.sqrt(d_k))

    if mask:
        for i in range(len(scores)):
            for j in range(len(scores[i])):
                if mask[i][j] == 0:
                    scores[i][j] = -1e9

    weights = [softmax(row) for row in scores]
    output = matmul(weights, V)

    return output, weights


def causal_mask(seq_len):
    """
    قناع السببية — كل كلمة تشوف الماضي فقط.

    مثال (seq_len=3):
        [[1, 0, 0],
         [1, 1, 0],
         [1, 1, 1]]
    """
    return [[1 if j <= i else 0 for j in range(seq_len)]
            for i in range(seq_len)]


# ═══════════════════════════════════════════════════════════
#  Multi-Head Attention
# ═══════════════════════════════════════════════════════════

class MultiHeadAttention:
    """Multi-Head Attention — عدة رؤوس انتباه"""

    def __init__(self, d_model, num_heads, seed=42):
        random.seed(seed)

        assert d_model % num_heads == 0, "d_model لازم يكون قابل للقسمة"

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        def rand_matrix(rows, cols):
            return [[random.gauss(0, 0.1) for _ in range(cols)]
                    for _ in range(rows)]

        self.W_q = rand_matrix(d_model, d_model)
        self.W_k = rand_matrix(d_model, d_model)
        self.W_v = rand_matrix(d_model, d_model)
        self.W_o = rand_matrix(d_model, d_model)

    def split_heads(self, X):
        seq_len = len(X)
        heads = []
        for h in range(self.num_heads):
            start = h * self.d_k
            end = start + self.d_k
            head = [row[start:end] for row in X]
            heads.append(head)
        return heads

    def forward(self, X, mask=None):
        Q = matmul(X, self.W_q)
        K = matmul(X, self.W_k)
        V = matmul(X, self.W_v)

        Q_heads = self.split_heads(Q)
        K_heads = self.split_heads(K)
        V_heads = self.split_heads(V)

        head_outputs = []
        all_weights = []

        for h in range(self.num_heads):
            out, weights = scaled_dot_product_attention(
                Q_heads[h], K_heads[h], V_heads[h], mask
            )
            head_outputs.append(out)
            all_weights.append(weights)

        seq_len = len(X)
        concatenated = []
        for i in range(seq_len):
            row = []
            for h in range(self.num_heads):
                row.extend(head_outputs[h][i])
            concatenated.append(row)

        output = matmul(concatenated, self.W_o)

        return output, all_weights


# ═══════════════════════════════════════════════════════════
#  Feed Forward
# ═══════════════════════════════════════════════════════════

class FeedForward:
    """شبكة عصبية بسيطة"""

    def __init__(self, d_model, d_ff, seed=42):
        random.seed(seed)

        def rand_matrix(rows, cols):
            return [[random.gauss(0, 0.1) for _ in range(cols)]
                    for _ in range(rows)]

        self.W1 = rand_matrix(d_model, d_ff)
        self.W2 = rand_matrix(d_ff, d_model)
        self.b1 = [0.0] * d_ff
        self.b2 = [0.0] * d_model

    def forward(self, X):
        h = matmul(X, self.W1)
        h = [[max(0, h[i][j] + self.b1[j]) for j in range(len(self.b1))]
             for i in range(len(h))]
        out = matmul(h, self.W2)
        out = [[out[i][j] + self.b2[j] for j in range(len(self.b2))]
               for i in range(len(out))]
        return out


# ═══════════════════════════════════════════════════════════
#  Layer Norm
# ═══════════════════════════════════════════════════════════

def layer_norm(X, eps=1e-6):
    result = []
    for row in X:
        mean = sum(row) / len(row)
        var = sum((x - mean) ** 2 for x in row) / len(row)
        std = math.sqrt(var + eps)
        result.append([(x - mean) / std for x in row])
    return result


# ═══════════════════════════════════════════════════════════
#  Transformer Block
# ═══════════════════════════════════════════════════════════

class TransformerBlock:
    """بلوك Transformer واحد"""

    def __init__(self, d_model, num_heads, d_ff, seed=42):
        self.attention = MultiHeadAttention(d_model, num_heads, seed)
        self.ff = FeedForward(d_model, d_ff, seed + 1)

    def forward(self, X, mask=None):
        attn_out, weights = self.attention.forward(X, mask)
        X = add(X, attn_out)
        X = layer_norm(X)

        ff_out = self.ff.forward(X)
        X = add(X, ff_out)
        X = layer_norm(X)

        return X, weights


# ═══════════════════════════════════════════════════════════
#  Transformer الكامل
# ═══════════════════════════════════════════════════════════

class Transformer:
    """Transformer مصغّر — تعليمي"""

    def __init__(self, vocab_size, d_model=16, num_heads=2,
                 d_ff=32, num_layers=1, seed=42):
        random.seed(seed)

        self.d_model = d_model
        self.vocab_size = vocab_size

        self.embedding = Embedding(vocab_size, d_model, seed)

        self.blocks = [
            TransformerBlock(d_model, num_heads, d_ff, seed + i)
            for i in range(num_layers)
        ]

        self.output_proj = [
            [random.gauss(0, 0.1) for _ in range(vocab_size)]
            for _ in range(d_model)
        ]

    def forward(self, token_ids):
        seq_len = len(token_ids)

        X = [self.embedding(tid) for tid in token_ids]

        pe = positional_encoding(seq_len, self.d_model)
        X = add(X, pe)

        mask = causal_mask(seq_len)

        all_weights = []
        for block in self.blocks:
            X, weights = block.forward(X, mask)
            all_weights.append(weights)

        logits = matmul(X, self.output_proj)

        return logits, all_weights


# ═══════════════════════════════════════════════════════════
#  العرض
# ═══════════════════════════════════════════════════════════

def main():
    print("═" * 65)
    print("  🧠 Transformer — النموذج الكامل (مصغّر)")
    print("═" * 65)
    print()

    vocab = ["<BOS>", "السلام", "عليكم", "مرحبا", "أهلاً"]
    vocab_size = len(vocab)

    print(f"المفردات ({vocab_size} كلمة):")
    for i, word in enumerate(vocab):
        print(f"  [{i}] {word}")
    print()

    print("تهيئة Transformer:")
    print(f"  d_model = 16")
    print(f"  num_heads = 2")
    print(f"  d_ff = 32")
    print(f"  num_layers = 1")
    print()

    model = Transformer(
        vocab_size=vocab_size,
        d_model=16,
        num_heads=2,
        d_ff=32,
        num_layers=1,
    )

    input_ids = [0, 1, 2]
    print(f"Input: {[vocab[i] for i in input_ids]}")
    print(f"IDs:   {input_ids}")
    print()

    print("─" * 65)
    print("Forward Pass:")
    print("─" * 65)
    print()

    logits, all_weights = model.forward(input_ids)

    print(f"عدد الطبقات: {len(all_weights)}")
    print(f"عدد الرؤوس: {len(all_weights[0])}")
    print()

    print("─" * 65)
    print("أوزان Attention (الطبقة الأولى، الرأس الأول):")
    print("─" * 65)
    print()

    weights = all_weights[0][0]
    for i, row in enumerate(weights):
        print(f"  '{vocab[input_ids[i]]}' تنتبه لـ:")
        for j, w in enumerate(row):
            bar = "█" * int(w * 30)
            print(f"    {vocab[input_ids[j]]:10} {w*100:5.1f}%  {bar}")
        print()

    print("─" * 65)
    print("Logits (للكلمة التالية بعد كل موضع):")
    print("─" * 65)
    print()

    for i, row in enumerate(logits):
        print(f"  بعد '{vocab[input_ids[i]]}':")
        for j, val in enumerate(row):
            print(f"    {vocab[j]:10} {val:+.4f}")
        print()

    print("─" * 65)
    print("🎯 التنبؤ بالكلمة التالية:")
    print("─" * 65)
    print()

    last_logits = logits[-1]
    probs = softmax(last_logits)

    print(f"بعد: {[vocab[i] for i in input_ids]}")
    print()

    indexed = sorted(enumerate(probs), key=lambda x: -x[1])
    for idx, prob in indexed:
        bar = "█" * int(prob * 40)
        print(f"  {vocab[idx]:10} {prob*100:5.1f}%  {bar}")

    print()
    print("═" * 65)
    print("  💡 الخلاصة:")
    print("═" * 65)
    print()
    print("  ✓ Transformer = Embedding + Attention + FF + Norm")
    print("  ✓ Attention = Q, K, V + Softmax")
    print("  ✓ Mask = لا يرى المستقبل")
    print("  ✓ Multi-Head = عدة رؤوس انتباه")
    print("  ✓ Output = Logits → Softmax → التنبؤ")
    print()
    print("  ⚠️  هذا النموذج **تعليمي** — بدون تدريب!")
    print("      الأوزان عشوائية — النتائج مو حقيقية.")
    print("      لكن **المعمارية** هي نفسها المستخدمة في")
    print("      جميع نماذج اللغة الحديثة.")
    print("      الفرق: الحجم (مليارات الأوزان) + التدريب.")
    print()


if __name__ == "__main__":
    main()
