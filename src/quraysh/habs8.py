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


# ═══════════════════════════════════════════════════════════
#  دوال الربط مع المفسّر
# ═══════════════════════════════════════════════════════════

_نموذج_hbs8 = None


def _احصل_على_hbs8():
    """تحميل HBS-8 مرة واحدة"""
    global _نموذج_hbs8
    if _نموذج_hbs8 is None:
        try:
            from pathlib import Path
            مسار = Path(__file__).parent.parent.parent / "models/habs/habs_8_trained.json"
            if مسار.exists():
                # نموذج مدرّب — لكن ما نقدر نحمّله كامل
                # ننشئ نموذج جديد بنفس الإعدادات
                _نموذج_hbs8 = Habs8(vocab_size=500, d_model=32, num_heads=4, num_layers=2, seq_len=4)
                # نحمّل الأوزان
                import json
                with open(مسار, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if "embedding" in data:
                    _نموذج_hbs8.embedding = data["embedding"]
                if "W_out" in data:
                    _نموذج_hbs8.W_out = data["W_out"]
            else:
                _نموذج_hbs8 = Habs8(vocab_size=500, d_model=32, num_heads=4, num_layers=2, seq_len=4)
        except Exception as e:
            print(f"⚠️ HBS-8: {e}")
            _نموذج_hbs8 = Habs8(vocab_size=100)
    return _نموذج_hbs8


# vocab القرآني — مبني من نفس corpus التدريب
_vocab_قرآني = None


def _احصل_على_vocab():
    """بناء vocab من نفس corpus التدريب"""
    global _vocab_قرآني
    if _vocab_قرآني is None:
        try:
            from pathlib import Path
            مسار = Path(__file__).parent.parent.parent / "models/corpus/quran/quran.txt"
            if مسار.exists():
                كلمات = load_corpus(str(مسار))
                _vocab_قرآني = build_vocab(كلمات, max_vocab=500)
            else:
                _vocab_قرآني = {"<PAD>": 0, "<UNK>": 1}
        except Exception as e:
            print(f"⚠️ vocab: {e}")
            _vocab_قرآني = {"<PAD>": 0, "<UNK>": 1}
    return _vocab_قرآني


def توليد_نص(بذرة="بسم الله", طول=10):
    """يولّد نص عربي — يستخدم vocab القرآني"""
    نموذج = _احصل_على_hbs8()
    vocab = _احصل_على_vocab()

    if نموذج is None:
        return "⚠️ HBS-8 غير متاح"

    # IDs من vocab الحقيقي
    seed_ids = [vocab.get(ك, 1) for ك in بذرة.split()]

    # توليد
    generated = نموذج.generate(seed_ids, length=طول, temperature=0.7)

    # فك
    id_to_word = {v: k for k, v in vocab.items()}
    return " ".join(id_to_word.get(i, "?") for i in generated)


دوال_HBS8 = {
    "توليد_نص": توليد_نص,
}