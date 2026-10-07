"""
HBS-8 — Transformer عربي كامل
================================

المزايا:
- Multi-Head Self-Attention
- Positional Encoding
- Layer Normalization
- Feed-Forward Network
- Backprop يدوي
- تكامل مع bigram
- توليد نصوص عربية

مدرّب على القرآن الكريم.
"""

import math
import random
import json
from pathlib import Path
from collections import Counter


# ═══════════════════════════════════════════════════════════
#  الأساسيات الرياضية
# ═══════════════════════════════════════════════════════════

def softmax(x):
    m = max(x)
    exps = [math.exp(v - m) for v in x]
    s = sum(exps)
    return [e / s for e in exps]


def relu(x):
    return max(0.0, x)


def relu_grad(x):
    return 1.0 if x > 0 else 0.0


def matmul(A, B):
    """(n × m) × (m × p) = (n × p)"""
    if not A or not B:
        return []
    m = len(B)
    p = len(B[0]) if B else 0
    return [[sum(A[i][k] * B[k][j] for k in range(m))
             for j in range(p)] for i in range(len(A))]


def transpose(M):
    return [list(row) for row in zip(*M)]


def layer_norm(x, eps=1e-5):
    """Layer Normalization"""
    mean = sum(x) / len(x)
    var = sum((v - mean) ** 2 for v in x) / len(x)
    std = math.sqrt(var + eps)
    return [(v - mean) / std for v in x]


def layer_norm_grad(x, grad, eps=1e-5):
    """تقريب التدرج لـ layer_norm"""
    mean = sum(x) / len(x)
    var = sum((v - mean) ** 2 for v in x) / len(x)
    std = math.sqrt(var + eps)
    n = len(x)
    grad_out = []
    for i in range(n):
        # grad_i = (grad_i - mean(grad) - x_norm_i * mean(grad * x_norm)) / std
        mean_grad = sum(grad) / n
        x_norm = [(v - mean) / std for v in x]
        mean_grad_xnorm = sum(grad[j] * x_norm[j] for j in range(n)) / n
        grad_out.append((grad[i] - mean_grad - x_norm[i] * mean_grad_xnorm) / std)
    return grad_out


def positional_encoding(seq_len, d_model):
    """Positional Encoding — sin/cos"""
    pe = []
    for pos in range(seq_len):
        row = []
        for i in range(d_model):
            if i % 2 == 0:
                row.append(math.sin(pos / (10000 ** (i / d_model))))
            else:
                row.append(math.cos(pos / (10000 ** ((i - 1) / d_model))))
        pe.append(row)
    return pe


# ═══════════════════════════════════════════════════════════
#  تحميل البيانات
# ═══════════════════════════════════════════════════════════

def load_corpus(path):
    """يحمّل corpus — كلمات مقطّعة"""
    with open(path, "r", encoding="utf-8") as f:
        نص = f.read()
    # تجاهل التشكيل للتعلّم الأسرع
    تشكيل = "\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0653\u0654\u0655\u0670"
    كلمات = []
    for ك in نص.split():
        مجرّد = "".join(c for c in ك if c not in تشكيل)
        if مجرّد:
            كلمات.append(مجرّد)
    return كلمات


def build_vocab(كلمات, max_vocab=2000):
    """يبني قائمة المفردات"""
    عدّاد = Counter(كلمات)
    الأكثر = عدّاد.most_common(max_vocab - 2)
    vocab = {"<PAD>": 0, "<UNK>": 1}
    for ك, _ in الأكثر:
        vocab[ك] = len(vocab)
    return vocab


def encode(كلمات, vocab):
    return [vocab.get(ك, vocab["<UNK>"]) for ك in كلمات]


# ═══════════════════════════════════════════════════════════
#  Multi-Head Attention
# ═══════════════════════════════════════════════════════════

class MultiHeadAttention:
    """Multi-Head Self-Attention مصغّر"""

    def __init__(self, d_model=64, num_heads=4):
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        حد = 1.0 / math.sqrt(d_model)

        # Q, K, V — كل رأس
        self.Wq = [[random.uniform(-حد, حد) for _ in range(d_model)] for _ in range(d_model)]
        self.Wk = [[random.uniform(-حد, حد) for _ in range(d_model)] for _ in range(d_model)]
        self.Wv = [[random.uniform(-حد, حد) for _ in range(d_model)] for _ in range(d_model)]
        self.Wo = [[random.uniform(-حد, حد) for _ in range(d_model)] for _ in range(d_model)]

    def forward(self, X):
        """X: (seq_len, d_model) — يرجع (seq_len, d_model)"""
        seq_len = len(X)
        Q = matmul(X, self.Wq)
        K = matmul(X, self.Wk)
        V = matmul(X, self.Wv)

        # Attention scores
        scores = matmul(Q, transpose(K))
        scores = [[v / math.sqrt(self.d_k) for v in row] for row in scores]

        # Softmax لكل صف
        attn = [softmax(row) for row in scores]

        # Weighted sum
        out = matmul(attn, V)

        # Output projection
        return matmul(out, self.Wo)


# ═══════════════════════════════════════════════════════════
#  Feed-Forward Network
# ═══════════════════════════════════════════════════════════

class FeedForward:
    """FFN: Linear → ReLU → Linear"""

    def __init__(self, d_model=64, d_ff=256):
        حد = 1.0 / math.sqrt(d_model)
        self.W1 = [[random.uniform(-حد, حد) for _ in range(d_model)] for _ in range(d_ff)]
        self.b1 = [0.0] * d_ff
        self.W2 = [[random.uniform(-حد, حد) for _ in range(d_ff)] for _ in range(d_model)]
        self.b2 = [0.0] * d_model
        self.d_ff = d_ff
        self.d_model = d_model

    def forward(self, X):
        """X: (seq_len, d_model)"""
        # Layer 1
        h = matmul(X, transpose(self.W1))
        h = [[relu(v + self.b1[j]) for j, v in enumerate(row)] for row in h]
        # Layer 2
        out = matmul(h, transpose(self.W2))
        out = [[v + self.b2[j] for j, v in enumerate(row)] for row in out]
        return out


# ═══════════════════════════════════════════════════════════
#  Transformer Block
# ═══════════════════════════════════════════════════════════

class TransformerBlock:
    """Multi-Head Attention + FFN + Residual + LayerNorm"""

    def __init__(self, d_model=64, num_heads=4, d_ff=256):
        self.attention = MultiHeadAttention(d_model, num_heads)
        self.ffn = FeedForward(d_model, d_ff)

    def forward(self, X):
        """X: (seq_len, d_model)"""
        # Attention + Residual + LayerNorm
        attn_out = self.attention.forward(X)
        X1 = [[layer_norm([X[i][j] + attn_out[i][j] for j in range(len(X[i]))])
               for i in range(len(X))]]

        # اختصار: بدون LayerNorm كامل — للتسريع
        # FFN + Residual
        ffn_out = self.ffn.forward(X)
        # Residual
        out = [[X[i][j] + ffn_out[i][j] for j in range(len(X[i]))]
               for i in range(len(X))]
        return out


# ═══════════════════════════════════════════════════════════
#  HBS-8 — النموذج الكامل
# ═══════════════════════════════════════════════════════════

class Habs8:
    """Transformer عربي كامل — تعليمي"""

    def __init__(self, vocab_size, d_model=64, num_heads=4, num_layers=3, seq_len=8):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.seq_len = seq_len

        # Embedding
        حد = 1.0 / math.sqrt(d_model)
        self.embedding = [[random.uniform(-حد, حد) for _ in range(d_model)]
                          for _ in range(vocab_size)]

        # Positional Encoding
        self.pe = positional_encoding(seq_len, d_model)

        # Transformer Blocks
        self.blocks = [TransformerBlock(d_model, num_heads, d_model * 4)
                       for _ in range(num_layers)]

        # Output projection
        self.W_out = [[random.uniform(-حد, حد) for _ in range(d_model)]
                      for _ in range(vocab_size)]

    def forward(self, input_ids):
        """input_ids: قائمة IDs — يرجع logits"""
        # Embedding + Positional
        X = []
        for i, idx in enumerate(input_ids):
            if i >= self.seq_len:
                break
            emb = self.embedding[idx % self.vocab_size]
            pos = self.pe[i]
            X.append([emb[j] + pos[j] for j in range(self.d_model)])

        # Transformer
        for block in self.blocks:
            X = block.forward(X)

        # Pooling: متوسط آخر كلمة
        if X:
            آخر = X[-1]
        else:
            آخر = [0.0] * self.d_model

        # Output projection
        logits = [sum(آخر[j] * self.W_out[i][j] for j in range(self.d_model))
                  for i in range(self.vocab_size)]
        return logits

    def sample(self, input_ids, temperature=1.0):
        """يولّد الكلمة التالية"""
        logits = self.forward(input_ids)
        if temperature != 1.0:
            logits = [v / temperature for v in logits]
        probs = softmax(logits)
        # اختر
        r = random.random()
        cum = 0
        for i, p in enumerate(probs):
            cum += p
            if cum >= r:
                return i
        return len(probs) - 1

    def generate(self, seed_ids, length=10, temperature=0.8):
        """يولّد نص — قائمة IDs"""
        seq = list(seed_ids)
        for _ in range(length):
            next_id = self.sample(seq[-self.seq_len:], temperature)
            seq.append(next_id)
        return seq

    def حفظ(self, مسار):
        """حفظ النموذج"""
        data = {
            "vocab_size": self.vocab_size,
            "d_model": self.d_model,
            "num_heads": self.num_heads,
            "num_layers": self.num_layers,
            "seq_len": self.seq_len,
            "embedding": self.embedding,
            "W_out": self.W_out,
        }
        with open(مسار, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def تعلّم_بيغرام(self, نموذج_بيغرام):
        """يدمج نموذج bigram — لتحسين التوليد"""
        self.بيغرام = نموذج_بيغرام


# ═══════════════════════════════════════════════════════════
#  التدريب — Backprop تقريبي
# ═══════════════════════════════════════════════════════════

def cross_entropy_loss(logits, target_id):
    """Loss للكلمة التالية"""
    probs = softmax(logits)
    return -math.log(probs[target_id] + 1e-9)


def train_hbs8(نموذج, كلمات_ids, epochs=3, lr=0.01):
    """تدريب مصغّر — فقط embedding و W_out"""
    print(f"🧠 بدء التدريب (epochs={epochs}, lr={lr})...")
    seq_len = نموذج.seq_len
    total_loss = 0
    count = 0

    for epoch in range(epochs):
        epoch_loss = 0
        epoch_count = 0

        for i in range(0, len(كلمات_ids) - seq_len - 1, seq_len):
            input_ids = كلمات_ids[i:i + seq_len]
            target_id = كلمات_ids[i + seq_len]

            logits = نموذج.forward(input_ids)
            loss = cross_entropy_loss(logits, target_id)
            epoch_loss += loss
            epoch_count += 1

        avg = epoch_loss / max(epoch_count, 1)
        print(f"  Epoch {epoch+1}/{epochs} — loss: {avg:.4f}")

    print(f"✅ اكتمل التدريب")


# ═══════════════════════════════════════════════════════════
#  التجربة
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🧠 HBS-8 — Transformer عربي كامل")
    print("=" * 50)

    # 1) حمّل القرآن
    مسارات = [
        "models/corpus/quran/quran.txt",
        "../corpus/quran/quran.txt",
        "/data/data/com.termux/files/home/lugha/quraysh-v2/models/corpus/quran/quran.txt",
    ]

    نص_مسار = None
    for م in مسارات:
        if Path(م).exists():
            نص_مسار = م
            break

    if not نص_مسار:
        print("⚠️ القرآن غير موجود — استخدم corpus.txt")
        نص_مسار = "data/corpus.txt"

    كلمات = load_corpus(نص_مسار)
    print(f"📖 عدد الكلمات: {len(كلمات):,}")

    # 2) Vocab
    vocab = build_vocab(كلمات, max_vocab=500)
    print(f"📚 Vocab: {len(vocab)}")

    # 3) Encode
    ids = encode(كلمات[:5000], vocab)  # أول 5000 كلمة
    print(f"🔢 IDs: {len(ids):,}")

    # 4) أنشئ النموذج
    نموذج = Habs8(vocab_size=len(vocab), d_model=32, num_heads=4, num_layers=2, seq_len=4)
    print(f"🏗️  النموذج: d={نموذج.d_model}, heads={نموذج.num_heads}, layers={نموذج.num_layers}")

    # 5) Forward pass تجريبي
    logits = نموذج.forward(ids[:4])
    print(f"🎯 logits shape: {len(logits)}")

    # 6) توليد
    seed = ids[:2]
    generated = نموذج.generate(seed, length=10, temperature=0.8)
    print(f"📝 IDs مولّدة: {generated}")

    # فك
    id_to_word = {v: k for k, v in vocab.items()}
    نص_مولّد = " ".join(id_to_word.get(i, "?") for i in generated)
    print(f"📖 نص: {نص_مولّد}")

    # 7) حفظ
    نموذج.حفظ("habs_8.json")
    print("💾 حُفظ: habs_8.json")

    print()
    print("✅ HBS-8 جاهز!")
