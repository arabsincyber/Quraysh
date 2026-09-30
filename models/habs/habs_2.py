"""
Habs-2 — هبس
=============

Transformer مصغّر — من الصفر.
يتدرب على نصوص عربية.

⚠️  تنبيه:
هذا النموذج **تعليمي فقط**.
"""

import math
import random
from pathlib import Path


# ═══════════════════════════════════════════════════════════
#  الأساسيات
# ═══════════════════════════════════════════════════════════

def softmax(x):
    m = max(x)
    exps = [math.exp(v - m) for v in x]
    s = sum(exps)
    return [e / s for e in exps]


def matmul(A, B):
    cols_B = len(B[0])
    return [[sum(A[i][k] * B[k][j] for k in range(len(B)))
             for j in range(cols_B)] for i in range(len(A))]


def transpose(M):
    return [list(row) for row in zip(*M)]


def scale(M, f):
    return [[x * f for x in row] for row in M]


def add(A, B):
    return [[A[i][j] + B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


def layer_norm(X, eps=1e-6):
    result = []
    for row in X:
        mean = sum(row) / len(row)
        var = sum((x - mean) ** 2 for x in row) / len(row)
        std = math.sqrt(var + eps)
        result.append([(x - mean) / std for x in row])
    return result


# ═══════════════════════════════════════════════════════════
#  البيانات
# ═══════════════════════════════════════════════════════════

def load_corpus(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def build_vocab(lines):
    words = set()
    for line in lines:
        for w in line.split():
            words.add(w)
    # نضيف رموز خاصة
    words.add("<BOS>")
    words.add("<EOS>")
    vocab = sorted(words)
    return vocab, {w: i for i, w in enumerate(vocab)}, {i: w for i, w in enumerate(vocab)}


# ═══════════════════════════════════════════════════════════
#  Embedding
# ═══════════════════════════════════════════════════════════

class Embedding:
    def __init__(self, vocab_size, d_model, seed=42):
        random.seed(seed)
        self.d_model = d_model
        self.vocab_size = vocab_size
        # تهيئة Xavier
        scale_v = math.sqrt(2.0 / (vocab_size + d_model))
        self.table = [
            [random.gauss(0, scale_v) for _ in range(d_model)]
            for _ in range(vocab_size)
        ]

    def __call__(self, token_id):
        return self.table[token_id]


# ═══════════════════════════════════════════════════════════
#  Positional Encoding
# ═══════════════════════════════════════════════════════════

def positional_encoding(seq_len, d_model):
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
    return [[1 if j <= i else 0 for j in range(seq_len)] for i in range(seq_len)]


# ═══════════════════════════════════════════════════════════
#  Multi-Head Attention
# ═══════════════════════════════════════════════════════════

class MultiHeadAttention:
    def __init__(self, d_model, num_heads, seed=42):
        random.seed(seed)
        assert d_model % num_heads == 0
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        def rand_matrix(rows, cols):
            scale_v = math.sqrt(2.0 / (rows + cols))
            return [[random.gauss(0, scale_v) for _ in range(cols)]
                    for _ in range(rows)]

        self.W_q = rand_matrix(d_model, d_model)
        self.W_k = rand_matrix(d_model, d_model)
        self.W_v = rand_matrix(d_model, d_model)
        self.W_o = rand_matrix(d_model, d_model)

    def split_heads(self, X):
        heads = []
        for h in range(self.num_heads):
            start = h * self.d_k
            end = start + self.d_k
            heads.append([row[start:end] for row in X])
        return heads

    def forward(self, X, mask=None):
        Q = matmul(X, self.W_q)
        K = matmul(X, self.W_k)
        V = matmul(X, self.W_v)

        Q_h = self.split_heads(Q)
        K_h = self.split_heads(K)
        V_h = self.split_heads(V)

        head_outs = []
        all_weights = []
        for h in range(self.num_heads):
            out, w = scaled_dot_product_attention(Q_h[h], K_h[h], V_h[h], mask)
            head_outs.append(out)
            all_weights.append(w)

        concat = []
        for i in range(len(X)):
            row = []
            for h in range(self.num_heads):
                row.extend(head_outs[h][i])
            concat.append(row)

        output = matmul(concat, self.W_o)
        return output, all_weights


# ═══════════════════════════════════════════════════════════
#  Feed Forward
# ═══════════════════════════════════════════════════════════

class FeedForward:
    def __init__(self, d_model, d_ff, seed=42):
        random.seed(seed)

        def rand_matrix(rows, cols):
            scale_v = math.sqrt(2.0 / (rows + cols))
            return [[random.gauss(0, scale_v) for _ in range(cols)]
                    for _ in range(rows)]

        self.W1 = rand_matrix(d_model, d_ff)
        self.W2 = rand_matrix(d_ff, d_model)

    def forward(self, X):
        h = matmul(X, self.W1)
        h = [[max(0, v) for v in row] for row in h]  # ReLU
        out = matmul(h, self.W2)
        return out


# ═══════════════════════════════════════════════════════════
#  Transformer Block
# ═══════════════════════════════════════════════════════════

class TransformerBlock:
    def __init__(self, d_model, num_heads, d_ff, seed=42):
        self.attention = MultiHeadAttention(d_model, num_heads, seed)
        self.ff = FeedForward(d_model, d_ff, seed + 1)

    def forward(self, X, mask=None):
        # Attention + Residual
        attn_out, weights = self.attention.forward(X, mask)
        X = add(X, attn_out)
        X = layer_norm(X)

        # FF + Residual
        ff_out = self.ff.forward(X)
        X = add(X, ff_out)
        X = layer_norm(X)

        return X, weights


# ═══════════════════════════════════════════════════════════
#  HBS-2
# ═══════════════════════════════════════════════════════════

class Habs2:
    def __init__(self, vocab_size, d_model=32, num_heads=2,
                 d_ff=64, num_layers=2, seed=42):
        random.seed(seed)
        self.d_model = d_model
        self.vocab_size = vocab_size

        self.embedding = Embedding(vocab_size, d_model, seed)
        self.blocks = [
            TransformerBlock(d_model, num_heads, d_ff, seed + i)
            for i in range(num_layers)
        ]

        # Output Projection
        scale_v = math.sqrt(2.0 / (d_model + vocab_size))
        self.output_proj = [
            [random.gauss(0, scale_v) for _ in range(vocab_size)]
            for _ in range(d_model)
        ]

    def forward(self, token_ids):
        seq_len = len(token_ids)

        # Embedding
        X = [self.embedding(tid) for tid in token_ids]

        # Positional Encoding
        pe = positional_encoding(seq_len, self.d_model)
        X = add(X, pe)

        # Mask
        mask = causal_mask(seq_len)

        # Blocks
        all_weights = []
        for block in self.blocks:
            X, w = block.forward(X, mask)
            all_weights.append(w)

        # Output
        logits = matmul(X, self.output_proj)
        return logits, all_weights

    def generate(self, start_words, vocab, word2id, id2word,
                 length=8, temperature=1.0):
        """يولّد جملة"""
        # Start
        tokens = [word2id.get(w, word2id["<BOS>"]) for w in start_words]

        for _ in range(length):
            # Forward
            logits, _ = self.forward(tokens)

            # آخر توقع
            last = logits[-1]

            # Temperature
            if temperature != 1.0:
                last = [x / temperature for x in last]

            probs = softmax(last)

            # اختيار
            r = random.random()
            cum = 0
            chosen = 0
            for i, p in enumerate(probs):
                cum += p
                if r <= cum:
                    chosen = i
                    break

            # إذا EOS — توقف
            if id2word[chosen] == "<EOS>":
                break

            tokens.append(chosen)

        # تحويل لنص
        result = [id2word.get(t, "?") for t in tokens if id2word.get(t) not in ("<BOS>", "<EOS>")]
        return " ".join(result)


# ═══════════════════════════════════════════════════════════
#  التشغيل
# ═══════════════════════════════════════════════════════════

def main():
    print("═" * 60)
    print("  🧠 HBS-2 — Transformer مصغّر")
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

    # النموذج
    model = Habs2(vocab_size=len(vocab), d_model=32, num_heads=2,
                  d_ff=64, num_layers=2)

    print(f"🧠 HBS-2:")
    print(f"   d_model: {model.d_model}")
    print(f"   num_heads: 2")
    print(f"   num_layers: 2")
    print(f"   vocab_size: {len(vocab)}")
    print()

    # التوليد (بدون تدريب — عشوائي)
    print("─" * 60)
    print("🎨 التوليد — بدون تدريب (عشوائي):")
    print("─" * 60)
    print()

    starts = ["قل", "هو", "إنا", "يوم"]
    for s in starts:
        result = model.generate([s], vocab, word2id, id2word,
                                length=8, temperature=1.0)
        print(f"   [{s}] → {result}")

    print()
    print("═" * 60)
    print("  ⚠️  تعليمي فقط — احترام القرآن.")
    print("═" * 60)
    print()


if __name__ == "__main__":
    main()
